# main.py
from google.cloud import firestore, run_v2
from datetime import datetime, timedelta

def cleanup_services(request):
    db = firestore.Client()
    client = run_v2.ServicesClient()
    
    # Get all services
    services = db.collection('cloud_run_services').stream()
    
    for doc in services:
        data = doc.to_dict()
        created = data['created_at']
        ttl = data['ttl_hours']
        
        # Check if expired
        if datetime.now() > created + timedelta(hours=ttl):
            # Delete Cloud Run service
            name = f"projects/{data['project']}/locations/{data['region']}/services/{doc.id}"
            client.delete_service(name=name)
            
            # Delete Firestore doc
            doc.reference.delete()
    
    return 'OK'