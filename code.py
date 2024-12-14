import pygame
import math

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CURTAIN_WIDTH = 60
CURTAIN_HEIGHT = 40
START_Y = 50
RESTING_DISTANCE = 10
STIFFNESS = 0.5
MOUSE_INFLUENCE_SIZE = 20
MOUSE_TEAR_SIZE = 8
GRAVITY = 9.8

# PointMass class
class PointMass:
    def __init__(self, x, y, fixed=False):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.fixed = fixed
        self.connections = []

    def update(self, dt):
        if not self.fixed:
            # Verlet Integration for physics
            velocity_x = self.x - self.prev_x
            velocity_y = self.y - self.prev_y
            self.prev_x = self.x
            self.prev_y = self.y
            self.x += velocity_x
            self.y += velocity_y + GRAVITY * dt * dt

    def apply_constraint(self, width, height):
        # Constrain within screen boundaries
        self.x = max(0, min(width, self.x))
        self.y = max(0, min(height, self.y))

    def attach_to(self, other, resting_distance, stiffness):
        self.connections.append((other, resting_distance, stiffness))

    def solve_constraints(self):
        for other, resting_distance, stiffness in self.connections:
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance == 0:
                continue
            error = (resting_distance - distance) / distance
            correction = error * 0.5 * stiffness
            if not self.fixed:
                self.x -= correction * dx
                self.y -= correction * dy
            if not other.fixed:
                other.x += correction * dx
                other.y += correction * dy

    def draw(self, screen, color=(255, 255, 255)):
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)
        for other, _, _ in self.connections:
            pygame.draw.line(screen, color, (self.x, self.y), (other.x, other.y), 1)

# Curtain class
class Curtain:
    def __init__(self, width, height, start_y, resting_distance):
        self.points = []
        self.width = width
        self.height = height
        self.resting_distance = resting_distance
        self.create_points(start_y)

    def create_points(self, start_y):
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                pos_x = x * self.resting_distance
                pos_y = start_y + y * self.resting_distance
                fixed = (y == 0)  # Top row fixed
                point = PointMass(pos_x, pos_y, fixed)
                self.points.append(point)

                # Attach to left
                if x > 0:
                    point.attach_to(self.points[-2], self.resting_distance, STIFFNESS)
                # Attach to top
                if y > 0:
                    point.attach_to(self.points[-(self.width + 2)], self.resting_distance, STIFFNESS)

    def update(self, dt):
        for point in self.points:
            point.update(dt)
        for _ in range(5):  # Solve constraints multiple times for stability
            for point in self.points:
                point.solve_constraints()

    def apply_constraints(self, screen_width, screen_height):
        for point in self.points:
            point.apply_constraint(screen_width, screen_height)

    def draw(self, screen):
        for point in self.points:
            point.draw(screen)

    def interact_with_mouse(self, mouse_pos, left_click, right_click):
        for point in self.points:
            dx = point.x - mouse_pos[0]
            dy = point.y - mouse_pos[1]
            distance = dx ** 2 + dy ** 2

            # Mouse dragging (left click)
            if left_click and distance < MOUSE_INFLUENCE_SIZE ** 2:
                if not point.fixed:  # Move the point with the mouse
                    point.x = mouse_pos[0]
                    point.y = mouse_pos[1]

            # Mouse tearing (right click)
            if right_click and distance < MOUSE_TEAR_SIZE ** 2:
                point.connections = []  # Remove all connections

# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Interactive Curtain Simulation")
    clock = pygame.time.Clock()

    curtain = Curtain(CURTAIN_WIDTH, CURTAIN_HEIGHT, START_Y, RESTING_DISTANCE)
    running = True

    while running:
        dt = clock.tick(30) / 1000.0
        left_click, _, right_click = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update simulation
        curtain.update(dt)
        curtain.apply_constraints(SCREEN_WIDTH, SCREEN_HEIGHT)
        curtain.interact_with_mouse(mouse_pos, left_click, right_click)

        # Render
        screen.fill((0, 0, 0))
        curtain.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
