from django.test import TestCase
from bunnies.models import RabbitHole, Bunny
from django.contrib.auth import get_user_model
from foxes.models import Fox
from django.urls import reverse
from django.core.cache import cache

UserModel = get_user_model()

# Create your tests here.

class FoxTests(TestCase):

    def setUp(self) -> None:
        # we need an owner to create rabbitholes
        self.owner = UserModel.objects.create_user(
            username='owner', email='user@test.com', password='rabbits', is_superuser=True
        )

        # We'll make requests posing as a fox
        self.fox_user = UserModel.objects.create_user(
            username='reynard', email='reynard@example.com', password='foxy'
        )

        # We're currently located at the crowdcomms office in blandford, dorset.
        self.fox = Fox.objects.create(
            name='Reynard', user=self.fox_user, latitude=50.86772590337301, longitude=-2.1561114615494446
        )

        # Create a couple of rabbit holes
        self.hole1 = RabbitHole.objects.create(
            location="Lidl",
            owner=self.owner,
            latitude=50.871485624686215, 
            longitude=-2.1576088547493963
        )

        self.hole2 = RabbitHole.objects.create(
            location="Tennis Club",
            owner=self.owner,
            latitude=50.869040482882056, 
            longitude=-2.175457306594088
        )

        self.hole3 = RabbitHole.objects.create(
            location="Kimmeridge",
            owner=self.owner,
            latitude=50.613665134196346,
            longitude=-2.131158935435499
        )

        self.url = "/foxes/find-nearby-holes/"

    def tearDown(self) -> None:
        cache.clear()
        return super().tearDown()

    def test_must_be_a_fox(self):
        """
        We need to be a fox in order to try and sniff out rabbit holes
        """

        # Add a bunny so we have at least 1 populated hole for a 2XX response
        Bunny.objects.create(
            name="Flopsy",
            home=self.hole1
        )

        resp = self.client.get(self.url)
        assert resp.status_code == 401

        self.client.login(username="owner", password="rabbits")
        resp = self.client.get(self.url)
        assert resp.status_code == 403

        self.client.logout()
        self.client.login(username="reynard", password="foxy")
        resp = self.client.get(self.url)
        assert resp.status_code == 200
    
    def test_no_populated_rabbit_holes(self):
        """
        If there are no populated rabbit holes, then we get a 404 response
        """

        self.client.login(username="reynard", password="foxy")
        resp = self.client.get(self.url)
        assert resp.status_code == 404

    def test_get_closest_rabbit_hole_containing_rabbits(self):
        """
        As a fox, I can detect the nearest populated rabbit hole by sniffing the air from my
        current location. Just by the power of my nose, I can get the id, position and 
        distance to the nearest rabbit hole containing active rabbits. Empty rabbit holes
        are of no interest to me, so are excluded.
        """

        self.client.login(username="reynard", password="foxy")

        # A rabbit decides to move into the rabbithole by the seaside in 
        # Kimmeridge bay. It likes the sea air or something.
        Bunny.objects.create(
            home=self.hole3,
            name="Flopsy"
        )

        resp = self.client.get(self.url)
        assert resp.status_code == 200
        data = resp.json()

        assert data["location"] == self.hole3.location
        self.assertAlmostEqual(data['distance_km'], 28.304820586821673, 1)


    def test_multiple_populated_rabbit_holes(self):
        """
        If more than one rabbit is at home - we'll see the nearest hole which contains at least one rabbit.
        """

        self.client.login(username="reynard", password="foxy")

        # Flopsy moves in to hole3
        Bunny.objects.create(
            home=self.hole3,
            name="Flopsy"
        )
        

        resp = self.client.get(self.url)
        assert resp.status_code == 200
        data = resp.json()

        assert data["location"] == self.hole3.location
        self.assertAlmostEqual(data['distance_km'], 28.304820586821673, 1)
        assert data["compass_direction"] == "S"

        # Mopsy moves into hole1
        mopsy = Bunny.objects.create(
            home=self.hole1,
            name="Mopsy"
        )

        resp = self.client.get(self.url)
        assert resp.status_code == 200
        data = resp.json()

        assert data["location"] == self.hole1.location
        self.assertAlmostEqual(data['distance_km'], 0.4310656644081723, 1)
        assert data["compass_direction"] == "N"

        # If we decide to move, the closest populated rabbithole may change
        Fox.objects.filter(id=self.fox.id).update(latitude=50.6279085931459, longitude=-2.1310911171122577)
        resp = self.client.get(self.url)
        data = resp.json()

        assert data["location"] == self.hole3.location
        self.assertAlmostEqual(data['distance_km'], 1.5838097872012162, 1)
        assert data["compass_direction"] == "S"

    def test_speed(self):
        """
        As a highly-strung and hungry fox, I can't wait around for lengthy postgres
        database queries to complete, I need to know the nearest rabbit hole instantly
        so I can conserve my limited energy in the hunt.
        
        HINT: foxes are cunning and fast, they shouldn't appear in analytics
        """

        self.client.login(username="reynard", password="foxy")

        # CottonTail moves into hole3
        Bunny.objects.create(
            home=self.hole3,
            name="CottonTail"
        )
        
        # NOTE: This is deliberate, 2 queries is all you're allowed! :)
        # These foxes are demanding customers.
        with self.assertNumQueries(2):
            resp = self.client.get(self.url)
        
        assert resp.status_code == 200



