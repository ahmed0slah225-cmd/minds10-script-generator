from core.documents import select_page_range

def test_page_range():
    pages=[{"page":i,"text":str(i)} for i in range(1,6)]
    assert [x["page"] for x in select_page_range(pages,2,4)] == [2,3,4]
