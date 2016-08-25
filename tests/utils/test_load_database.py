import pytest

from loqusdb.utils import load_database
from loqusdb.exceptions import CaseError

def test_load_database(vcf_path, ped_path, mongo_adapter):
    db = mongo_adapter.db
    
    load_database(
        adapter=mongo_adapter, 
        variant_file=vcf_path, 
        family_file=ped_path, 
        family_type='ped', 
        bulk_insert=False
    )
    
    mongo_case = db.case.find_one()
    
    assert mongo_case['case_id'] == 'recessive_trio'

def test_load_database_wrong_ped(vcf_path, funny_ped_path, mongo_adapter):
    db = mongo_adapter.db
    
    with pytest.raises(CaseError):
        load_database(
            adapter=mongo_adapter, 
            variant_file=vcf_path, 
            family_file=funny_ped_path, 
            family_type='ped', 
            bulk_insert=False
        )
    
