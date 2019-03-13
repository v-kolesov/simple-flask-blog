def test_page_create(client):
    rsp = client.post('/admin/pages/none', data={
        'title': 'Title',
        'is_public': True,
        'slug': 'text-slug',
        'text': 'Text',
        })
    assert rsp.status_code == 302
    assert rsp.location is not None
