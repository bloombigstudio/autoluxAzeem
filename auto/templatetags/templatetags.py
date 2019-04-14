from django import template

register = template.Library()

# @register.simple_tag
# def relative_url(value, field_name, urlencode=None):
#     url = '?{}={}'.format(field_name, value)
#     if urlencode:
#         querystring = urlencode.split('&')
#         filtered_querystring = filter(lambda p: (p.split('=')[0] != field_name, querystring)
#         encoded_querystring = '&'.join(filtered_querystring)
#         url = '{}&{}'.format(url, encoded_querystring)
#     return url

# @register.simple_tag(takes_context=True)
# def query_transform(context, **kwargs):
#     '''
#     Returns the URL-encoded querystring for the current page,
#     updating the params with the key/value pairs passed to the tag.
#
#     E.g: given the querystring ?foo=1&bar=2
#     {% query_transform bar=3 %} outputs ?foo=1&bar=3
#     {% query_transform foo='baz' %} outputs ?foo=baz&bar=2
#     {% query_transform foo='one' bar='two' baz=99 %} outputs ?foo=one&bar=two&baz=99
#
#     A RequestContext is required for access to the current querystring.
#     '''
#     query = context['request'].GET.copy()
#     for k, v in kwargs.items():
#         query[k] = str(v)
#     return query.urlencode()

# @register.simple_tag
# def query_transform(context, **kwargs):
#     updated = context['request'].GET.copy()
#     for k, v in kwargs.items():
#         if v is not None:
#             updated[k] = v
#         else:
#             updated.pop(k, 0)  # Remove or return 0 - aka, delete safely this key
#
#     return updated.urlencode()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Tim``)::

        {% querystring "name"="Diego" "age"=20 %}
        ?name=Diego&gender=male&age=20
    """
    request = context['request']
    updated = request.GET.copy()

    # for param in list(updated):
    #     if updated[param] == '':
    #         del updated[param]

    for k, v in kwargs.items():  # have to iterate over and not use .update as it's a QueryDict not a dict
        updated[k] = str(v)

    return '?{}'.format(updated.urlencode()) if updated else ''