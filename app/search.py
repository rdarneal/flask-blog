from flask import current_app

def add_to_index(index, model):
    # check if elastic search is available
	if not current_app.elasticsearch:
		return
	# create a dictionary of the fields to be indexed
	payload = {}
	for field in model.__searchable__:
		payload[field] = getattr(model, field)
	current_app.elasticsearch.index(index=index, id=model.id, body=payload)
 
def remove_from_index(index, model):
    # check if elastic search is available
    if not current_app.elasticsearch:
        return
    # delete the index
    current_app.elasticsearch.delete(index=index, id=model.id)
    
def query_index(index, query, page, per_page):
    # check if elastic search is available
	if not current_app.elasticsearch:
		return [], 0
	# search the index
	search = current_app.elasticsearch.search(
		index=index,
		# use multi_match to search all fields, use * to search entire index
		body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
			  'from': (page - 1) * per_page, 'size': per_page})
	# extract the id values from the search results
	ids = [int(hit['_id']) for hit in search['hits']['hits']]
	# return the list and the total number of results
	return ids, search['hits']['total']['value']