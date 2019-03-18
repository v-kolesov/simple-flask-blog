import pytest
from models import db, Page


def test_page_create(client):
    rsp = client.post('/admin/pages/none', data={
        'title': 'Title',
        'is_public': True,
        'slug': 'text-slug',
        'text': 'Text',
        })
    assert rsp.status_code == 302
    assert rsp.location is not None


@pytest.mark.parametrize("is_published,preview,http_code", (
    (True, None, 200),
    (True, '1', 200),
    (False, '1', 200),
    (False, None, 404),
))
def test_get_slug(client, is_published, preview, http_code):
    page = Page(
        slug='test',
        is_published=is_published,
        title='test',
        text='text'
    )
    db.session.add(page)
    db.session.commit()
    if preview is not None:
        url = f'/test.html?preview={preview}'
    else:
        url = '/test.html'

    assert client.get(url).status_code == http_code
    db.session.delete(page)
    db.session.commit()
