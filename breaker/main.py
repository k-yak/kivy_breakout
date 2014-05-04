import kivy
kivy.require('1.1.3')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.floatlayout import FloatLayout

import particlesystem as kivyparticle


class Breaker(FloatLayout):
    pass


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_fps, 0.5)

    def update_fps(self, dt):
        self.fps = str(int(Clock.get_fps()))


class BreakerPaddle(Widget):
    score = NumericProperty(0)
    max_velocity = 10

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_x - self.center_x) / (self.width / 10)
            bounced = Vector(vx, -1 * vy)

            if (abs(bounced.x) < self.max_velocity) and (abs(bounced.y) < self.max_velocity):
                bounced *= 1.1

            ball.velocity = bounced.x + offset, bounced.y


class BreakerBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class BreakerBrick(Widget):
    particle = None
    game = None

    def particle_explode(self, game):
        self.game = game
        self.particle = kivyparticle.ParticleSystem("particles/brick_explode.pex")
        self.particle.move(self.center_x, self.center_y)
        self.particle.emitter_x_variance = self.width / 2
        self.particle.start(1)
        game.add_widget(self.particle)

    def collide(self, game, ball):
        if self.collide_widget(ball):
            # Bounce
            vx, vy = ball.velocity
            offset = (ball.center_x - self.center_x) / (self.width / 10)
            bounced = Vector(vx, -1 * vy)
            ball.velocity = bounced.x + offset, bounced.y

            # Particle explode
            self.particle_explode(game)

            # Remove brick
            game.bricks.remove(self)
            game.remove_widget(self)


class BreakerGame(Widget):
    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    brick = ObjectProperty(None)
    brick2 = ObjectProperty(None)
    brick3 = ObjectProperty(None)
    bricks = []

    def ini_bricks(self):
        self.bricks.append(self.brick)
        self.bricks.append(self.brick2)
        self.bricks.append(self.brick3)

    def serve_ball(self, velocity=(0, 4)):
        self.ball.center_x = self.player.center_x
        self.ball.center_y = self.player.height + self.ball.height
        self.ball.velocity = velocity

    def update(self, dt):
        self.ball.move()

        # Bounce of paddles
        self.player.bounce_ball(self.ball)

        # Brick collision
        for brickItem in self.bricks:
            brickItem.collide(self, self.ball)


        # Bounce ball off top
        if self.ball.top > self.top:
            self.ball.velocity_y *= -1

        # Bounce ball off left or right
        if (self.ball.x < self.x) or (self.ball.right > self.right):
            self.ball.velocity_x *= -1

        # Ball lost
        if self.ball.y < self.y:
            self.serve_ball()

    def on_touch_move(self, touch):
        if touch.y < (self.height / 2):
            if (touch.x + self.player.width / 2) > self.width:
                self.player.center_x = self.width - (self.player.width / 2)
            else:
                if (touch.x - self.player.width / 2) < 0:
                    self.player.center_x = self.player.width / 2
                else:
                    self.player.center_x = touch.x


class BreakerApp(App):
    def build(self):
        game = BreakerGame()
        game.ini_bricks()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game

if __name__ in ('__main__', '__android__'):
    BreakerApp().run()