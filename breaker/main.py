import kivy
kivy.require('1.1.3')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout


class Breaker(FloatLayout):
    pass


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


class BreakerGame(Widget):
    ball = ObjectProperty(None)
    player = ObjectProperty(None)

    def serve_ball(self, vel = (0, 4)):
        self.ball.center_x = self.player.center_x
        self.ball.center_y = self.player.height + self.ball.height
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        # Bounce of paddles
        self.player.bounce_ball(self.ball)

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
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ in ('__main__', '__android__'):
    BreakerApp().run()