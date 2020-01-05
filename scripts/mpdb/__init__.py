# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:39:27'

"""

"""
import os
import sys
DIR = os.path.dirname(__file__)
try:
    import Qt
except:
    _vendor_path = os.path.join(DIR,"_vendor")
    sys.path.append(_vendor_path)
    import Qt

from MPdb import set_trace

