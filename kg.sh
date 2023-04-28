export PYTHONUNBUFFERED=1 JWT_SECRET='test' RABBIT_PASSWORD='' RABBIT_USER=guest HOST=localhost:8000 USE_STORAGE_S3=False ON_PREM=True 	STRIPE_TEST_SECRET_KEY=sk_test_abc
export HOST=localhost:8000 JWT_SECRET='test' NEO4J_HOST=localhost NEO4J_PASSWORD=aZ3vVHrpxMQv99e8 NEO4J_USER=neo4j ON_PREM=True PYTHONUNBUFFERED=1 RABBIT_PASSWORD='' RABBIT_USER=guest STRIPE_TEST_SECRET_KEY=sk_test_abc USE_KNOWLEDGE_GRAPH=True USE_STORAGE_S3=False

python /home/dhruv/Desktop/DeepVA/deepva-api/deep_va/manage.py kg_import_wikidata_ids --ids $(cat /home/dhruv/Desktop/Uni/nlp_stuff/test_unique_entities_list2.txt)