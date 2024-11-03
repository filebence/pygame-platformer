import pygame, random
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768

class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.pos = pos
        self.color = random.choice(["red", "green", "blue", "yellow", "brown", "orange", "purple"])
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.direction = self.direction.normalize()
        self.speed = random.randint(50, 400)
        self.alpha = 255
        self.fade_speed = 700
        self.create_surf()

    def create_surf(self):
        self.image = pygame.Surface((4, 4)).convert_alpha()
        self.image.set_colorkey("black")
        pygame.draw.circle(self.image, self.color, (2, 2), 4)
        self.rect = self.image.get_frect(center = self.pos)

    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
    
    def fade(self, dt):
        self.alpha -= self.fade_speed * dt
        self.image.set_alpha(self.alpha)
    
    def check_pos(self):
        if (self.rect.right <= 0 or
            self.rect.left >= SCREEN_WIDTH or
            self.rect.bottom <= 0 or
            self.rect.top >= SCREEN_HEIGHT) or self.alpha <= 0: self.kill()

    def update(self, dt):
        self.move(dt)
        self.fade(dt)
        self.check_pos()

class Particle2(pygame.sprite.Sprite):

    def __init__(self, groups, start_pos, end_pos, direction):
        super().__init__(groups)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.direction = direction
        self.speed = 50
        self.image = pygame.Surface((4, 4)).convert_alpha()
        self.rect = self.image.get_frect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT))
        self.image.fill((255, 0, 0))
        self.last_tick = pygame.time.get_ticks()

    def move(self, dt):
        self.rect.x -= self.direction[0] * self.speed * dt
        self.rect.y -= self.direction[1] * self.speed * dt
        pygame.draw.circle(self.image, "black", (2, 2), 2)

    def check_pos(self):
        if self.rect.top <= self.end_pos:
            self.kill()
            spawn_particles(self.rect.center)

    def update(self, dt):
        self.move(dt)
        self.check_pos()
    
def spawn_particles(pos):
    for _ in range(1000):
        Particle(particle_group, pos)

def spawn_particles2(start_pos, end_pos, direction):
    Particle2(particle2_group, start_pos, end_pos, direction)

particle_group = pygame.sprite.Group()
particle2_group = pygame.sprite.Group()