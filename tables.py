from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1beta1 import (
    ArrayUnion,
    CollectionReference,
    DocumentReference,
)

from constants import ACCOUNT_CREATE_TRANSACTION_TYPE as ACCOUNT_CREATE
from constants import ANALYTICS, ANALYTICS_FIELDS
from constants import DATA_MANAGE_TRANSACTION_TYPE as DATA_MANAGE
from constants import DB_ACTION_READ_TYPE as READ_TYPE
from constants import DB_ACTION_WRITE_TYPE as WRITE_TYPE
from constants import SITE_DATA, SITE_META
from credentials_manager import get_creds
from db_queries import DbManager
from utils import (
    c_print,
    check_password_hash,
    gen_site_id,
    get_site_host,
    hash_password,
    now,
)

cred = credentials.Certificate(get_creds())
c_print("--Initializing app--", "header")
firebase_admin.initialize_app(cred)
cred.get_access_token()
c_print("--app ready--", "header")
db = firestore.client()
c_print("--Creating DbManager Instance--", "header")
manager: DbManager = DbManager(db)


class RequestParser(object):
    def __err_msg(self, name):
        return self._err(f"Invalid type of data sent for key - {name}")

    def _err(self, name):
        return {"error": name}

    def __initial_request_validator(self):
        """Internal method..checks for the existance of previous accounts
            and makes sure valid type of request is provided
        """
        origin: str = self.js_data.get("$origin", "")
        site_id: str = self.js_data.get("site_id")
        transaction_type: str = self.js_data.get("transaction_type")
        if not transaction_type or not site_id or not origin:
            return {"result": False, "message": self._err("Invalid Values provided")}
        if (
            not manager.is_site_registered(origin)
            and transaction_type != ACCOUNT_CREATE
        ):
            return {"result": False, "message": self._err("Site Not Registered")}
        self.origin = origin
        self.site_id = site_id
        return {"result": True}

    def _manage_db_data(self):
        """Return Data based on request..reading the data will check for the site ID and return response
            only if the password is provided. Writing the data will take the site_id
        """
        data_action: int = self.js_data.get("db_action")
        if data_action == READ_TYPE:
            """Read the data. Should only be uswed in the dashboard or data.pycode.tk"""
            pw: str = self.js_data.get("password", "")
            if not pw:
                return self._err("No Password Provided")
            meta_doc: DocumentReference = manager.get_document(
                f"/{SITE_META}/{self.origin}"
            )
            if not manager.document_exists(meta_doc):
                return self._err("Incorrect username or password")
            site_id = meta_doc.get().get("site_id")
            if not check_password_hash(meta_doc.get, pw):
                return self._err("Incorrect username or password")

            doc: CollectionReference = manager.get_collection(
                f"/{SITE_DATA}/{site_id}/{ANALYTICS}"
            )
            if not manager.document_exists(doc):
                return self._err("No analytics for the given document")
            return {"data": doc.get().to_dict()}
        if data_action == WRITE_TYPE:
            """js_data should be a dictionary with the keys:
            INTERNAL_JSON_CONFIG_DATA,INDIVIDUAL_VISIT_DATA,SESSION_STORAGE_DATA
            """
            exclude_updates_for: list = self.js_data.get("exclude", [])
            _site_id: str = manager.get_document(
                f"{SITE_META}/{self.origin}"
            ).get().get("site_id")
            if _site_id != self.site_id:
                return self._err("Invalid Site ID")
            doc: DocumentReference = manager.get_document(f"{SITE_DATA}/{self.site_id}")
            col: CollectionReference = doc.collection(ANALYTICS)
            analytics_arr: DocumentReference = col.document("VISITOR_DATA")
            internal_arr: DocumentReference = col.document("INTERNAL_DATA")
            actions_arr: DocumentReference = col.document("ACTIONS")
            analytics_arr_exists = manager.document_exists(analytics_arr)
            doc.set({"last_update_from_backend": now()})
            visit_id = self.js_data.get("visit_id")
            for field in ANALYTICS_FIELDS:
                name: str = field.get("NAME")
                if name in exclude_updates_for:
                    continue
                set_by_server: bool = field.get("SET_BY_SERVER", False)
                expected_type: Any = field.get(
                    "EXPECTED_TYPE"
                )  # Check for malformed input..like [object Object]
                if name not in self.js_data and not set_by_server:
                    return self._err(f"Required Field Missing - {name}")
                if set_by_server:
                    """Values that will be set by the server..like VIEW_COUNT"""
                    data_fields: DocumentReference = col.document(name)
                    if name == "VIEW_COUNT" and self.js_data.get("update_view_count"):
                        if manager.document_exists(data_fields):
                            data_fields.update(
                                {"value": data_fields.get().get("value") + 1}
                            )
                        else:
                            data_fields.set(
                                {"value": data_fields.get().get("value") + 1}
                            )
                        continue
                if name == "INTERNAL_JSON_CONFIG_DATA":
                    """internal json data including errors"""
                    config = self.js_data[name]
                    if not isinstance(config, expected_type):
                        return self.__err_msg(name)
                    internal_arr.set({name: {visit_id: config}}, merge=True)
                    continue
                if name == "INDIVIDUAL_VISIT_DATA":
                    """Indiviual user data including session tokens, user agent, 
                    time spent on the site (sent during window.onunload  or other event specified by the user
                    """
                    visit_data = self.js_data[name]
                    visit_data["id"] = visit_id
                    visit_data["addr"] = self.headers.get("X-Forwarded-For")
                    if not isinstance(visit_data, expected_type):
                        return self.__err_msg(name)
                    if analytics_arr_exists:
                        analytics_arr.update({name: ArrayUnion([visit_data])})
                    else:
                        analytics_arr.set({name: [visit_data]}, merge=True)
                        analytics_arr_exists = True
                    continue
                if name == "SESSION_STORAGE_DATA":
                    """Session storage data.. useful for tracking session times and visit counters"""
                    sess_data = self.js_data[name]
                    sess_data["id"] = visit_id
                    if not isinstance(sess_data, expected_type):
                        return self.__err_msg(name)
                    if analytics_arr_exists:
                        analytics_arr.update({name: ArrayUnion([sess_data])})
                    else:
                        analytics_arr.set({name: [sess_data]}, merge=True)
                        analytics_arr_exists = True
                    continue
                if name == "ACTIONS":
                    action_data = self.js_data.get(name)
                    if not action_data:
                        continue
                    if not isinstance(action_data, expected_type):
                        return self.__err_msg(name)
                    if manager.document_exists(actions_arr):
                        actions_arr.update({name: ArrayUnion([action_data])})
                    else:
                        actions_arr.set({name: [action_data]})
                    continue
            return {"success": True}
        else:
            return self._err("bad data_action type")

    @staticmethod
    def register_site(_site_origin: str, pw: str):
        """register site if it does not exist
        
        Args:
            _site_origin (str): origin of the website i.e subdomain.domain.com
            pw (str): password for the account
        
        Returns:
            bool
        """

        site_id = gen_site_id()
        site_origin: str = get_site_host(_site_origin)
        _hash = hash_password(pw)
        if manager.is_site_registered(site_origin):
            return {"error": "Site Already Registered"}
        doc: DocumentReference = manager.get_document(f"/{SITE_META}/{site_origin}/")
        doc.set(
            {"account_creation": now(), "site_id": site_id, "hashedPassword": _hash}
        )
        return True

    def parse_request(self, js_data: dict, headers: dict) -> int:
        """parsed a request made by the user..preferred method is post
        
        Args:
            js_data (dict): form data
            headers (dict): request headers
        
        Returns:
            [dict]: json response to be sent back to the client
        """
        self.headers: dict = headers
        self.js_data: dict = js_data
        init_data: dict = self.__initial_request_validator()
        result: bool = init_data["result"]
        if not result:
            return init_data["message"]
        return self._manage_db_data()
