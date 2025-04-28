from django.shortcuts import render
from django.core.cache import cache  # Import from cache


def counter(request):
    count = cache.get("counter", 0)  # Get counter from cache or set to 0
    count += 1
    cache.set("counter", count, timeout=3600)  # Cache expires in 1 hour

    context = {"count": count}
    return render(request, "counter/counter.html", context)
