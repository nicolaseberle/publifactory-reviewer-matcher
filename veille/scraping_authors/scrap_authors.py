import scholarly

search_query = scholarly.search_keyword('biology organic')

#print(len(list(search_query)))

print(next(search_query))
print(next(search_query))
print(next(search_query))
print(next(search_query))
