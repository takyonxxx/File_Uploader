# -*- coding: utf-8 -*-

import os
from pathlib import Path

from document.lemmatizer import Lemmatizer

from document.models import Document

lemmatizer = Lemmatizer()

ROOT_PATH = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = ROOT_PATH / 'document'


def get_file_extension(doc_id):
    document = Document.objects.filter(id=doc_id).first()
    if document:
        doc_name = document.name
        ext = os.path.splitext(doc_name)[-1].upper()
        return ext
