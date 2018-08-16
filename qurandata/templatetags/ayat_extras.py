from django import template

register = template.Library()

@register.filter
def batch(iterable, n=1):
    l = len(iterable[0])
    a, b, c = iterable
    for ndx in range(0, l, n):
        yield a[ndx:min(ndx + n, l)], zip(b[ndx:min(ndx + n, l)], c[ndx:min(ndx + n, l)])