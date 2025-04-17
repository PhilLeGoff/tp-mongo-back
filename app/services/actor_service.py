from app.models.actor import Actor

class ActorService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_actor_details(self, actor_id):
        try:
            return Actor.get_details(self.mongo, actor_id)
        except Exception as e:
            print("❌ Error fetching actor details:", e)
            return None
