"""small helper functions for tables.py"""
# Firebase implicitly creates a new entry if it doesn't exist so no need for a
# create_data method we will add it assuming it already exists
from typing import List, Optional, Union

from google.cloud.firestore_v1beta1 import CollectionReference, DocumentReference

from constants import SITE_DATA, SITE_META
from utils import c_print


class DbManager(object):
    __doc__ = "Basic Database Manager with some helpful methods"
    _verbose: bool = False

    @classmethod
    def _filter_func(
        self, path: str, return_iterator: Optional[bool] = False
    ) -> Union[str, list]:
        fx = lambda x: x
        arr = path.split("/")
        filter_obj = filter(fx, arr)
        return filter_obj if return_iterator else list(filter_obj)

    def __init__(self, db_instance):
        self.db = db_instance

    def _debug(self, s: str) -> None:
        return c_print(s, "OKBLUE") if self._verbose else None

    def _document_exists_string(self, doc_path: str) -> bool:
        """Useful for checking if the document exists and does it potentially have data or not
        
        Args:
            doc_path (str): path of the document seperated by "/"
        
        Returns:
            bool
        """
        return self.get_document(doc_path).get().exists

    def document_exists(self, doc_path: Union[str, DocumentReference]) -> bool:
        """returns True if document exists
        
        Args:
            doc_path (Union[str, DocumentReference]): document reference or string
        
        Returns:
            bool
        """

        if isinstance(doc_path, str):
            return self._document_exists_string(doc_path)
        return doc_path.get().exists

    def is_site_registered(self, site_id: str) -> bool:
        """Returns a bool and checks for the site in the site_meta section. 
        doesn't matter if the site has any analytics or not
        
        Args:
            site_id (str): Id of the website registered
        
        Returns:
            bool
        """
        return self.document_exists(f"{SITE_META}/{site_id}")

    def _get_collection_or_document(
        self, db_path: Union[List[str], str]
    ) -> Union[DocumentReference, CollectionReference]:
        """Accepts a db_path - a string of /collection/document/ pairs to get attribute from
            Internal method..does not take care of any error handling and edge cases
            Use DbManager.get_collection() for collections and DbManager.get_document() instead
        
        Args:
            db_path (Union[List[str], str]): either path of the document as a string or list of document
            collectio pairs to iterate through
        
        Raises:
            Exception: exception is raised when document or a collection is accessed at invalid position
        
        Returns:
            Union[DocumentReference, CollectionReference]: returns either DocumentReference or CollectionReference 
            depending on the path requestede
        """

        pair: list
        if isinstance(db_path, str):
            pair = self._filter_func(db_path)
        else:
            pair = db_path
        curr_value = None
        self._debug(
            f"Expected return: {'collection' if len(pair)%2==0 else 'document'}"
        )
        i = 0
        for inst in pair:
            if i % 2 == 0:
                self._debug(f"Looking up a collection with name - {inst}")
                if curr_value is None:
                    curr_value = self.db.collection(inst)
                else:
                    curr_value = curr_value.collection(inst)
            else:
                self._debug(f"Looking up a collection with name - {inst}")
                if curr_value is None:
                    raise Exception(f"Cannot have document at odd position - {i}")
                curr_value = curr_value.document(inst)
            i += 1
        return curr_value

    def get_collection(self, path: str) -> CollectionReference:
        """Returns a Collection object from the database.
         Does not check for the existence of the data
        :Example: collection = manager_instance.get_collection("/collection/document/inner_collection")
        trailing and leading slashes are not required
        Args:
            path (str): path to get collection from
        
        Raises:
            ValueError: raised length of collection required is odd
        
        Returns:
            CollectionReference
        """

        pair = self._filter_func(path)
        if (len(pair) - 1) % 2 == 0:
            return self._get_collection_or_document(pair)
        else:
            raise ValueError("Length of collection should be even")

    def get_document(self, path: str) -> DocumentReference:
        """Returns a document reference from the database. Does not check for the existence of the data
        use DbManager.document_exists(path) for that.

        :example: document = manager_instance.get_document("/collection/document/inner_collection/inner_document/)

        trailing and leading slashes are not required
        """
        pair = self._filter_func(path)
        if (len(pair) - 1) % 2 == 0:
            raise ValueError("Length of document should be odd")
        else:
            return self._get_collection_or_document(pair)
