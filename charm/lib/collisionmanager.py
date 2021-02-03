def collide_objects(obj, others):
    """Return a list of objects that collide with the first object"""
    # Setup comparison dict (https://www.pygame.org/docs/ref/rect.html#pygame.Rect.collidedictall)
    other_dicts = {tuple(other.collision_box): other for other in others if other is not obj}
    # Get all the collisions (as a list of (rect, obj) tuples)
    collisions = obj.collision_box.collidedictall(other_dicts)
    # Convert to list of objects
    collisions_objs = [obj for rect, obj in collisions]
    return collisions_objs


class CollisionManager():
    def __init__(self):
        # A dictionary mapping each object to everything it has collided with
        self.collisions = {}

    def reset(self):
        """Clear cached collisions from previous frame"""
        self.collisions = {}

    def __getitem__(self, obj):
        """Convenient way to pull up collisions for a particular object"""
        return self.collisions[obj]

    def __len__(self):
        lengths = [len(v) for v in self.collisions.values()]
        sums = sum(lengths)
        halfsums = sums / 2
        return int(halfsums)

    def update(self, collidables, projectiles):
        """Calculate collisions for every object with a `.collision_box` attribute for this frame"""
        # Clear cached collisions
        self.reset()

        # https://www.pygame.org/docs/ref/rect.html#pygame.Rect.collidedictall
        collidables = [c for c in collidables if c.collision_box is not None]
        projectiles = [p for p in projectiles if p.collision_box is not None]

        # Collide collidables with collidables and projectiles
        for c in collidables:
            c_collisions = collide_objects(c, collidables)
            p_collisions = collide_objects(c, projectiles)
            self.collisions[c] = c_collisions + p_collisions

        # Collide projectiles with collidables
        for p in projectiles:
            c_collisions = collide_objects(p, collidables)
            self.collisions[p] = c_collisions
