import pygame
import neat
import time
import os
import random


pygame.font.init()

DISPLAY_WIDTH = 570
DISPLAY_HEIGHT = 800
BASE_HEIGHT = 750
GAME_SPEED = 8
SCORE_FONT = pygame.font.SysFont("comicsans", 40)
gen = 0

BIRD_IMG = [pygame.transform.scale2x(pygame.image.load("./imgs/bird1.png")), pygame.transform.scale2x(pygame.image.load("./imgs/bird2.png")), pygame.transform.scale2x(pygame.image.load("./imgs/bird3.png"))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load("./imgs/pipe.png"))
BASE_IMG = pygame.transform.scale2x(pygame.image.load("./imgs/base.png"))
BG_IMG = pygame.transform.scale2x(pygame.image.load("./imgs/bg.png"))

class Bird:
    IMGS = BIRD_IMG
    MAX_ROT = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    VELOCITY = -10.5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = self.VELOCITY
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.velocity*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16
        if d <= 0:
            d -= 2
        self.y = self.y + d

        if d<0 or self.y<self.height + 50:
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotate_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotate_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotate_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)




class Pipe:
    GAP = 200
    VEL = GAME_SPEED

    def __init__(self, x):
        self.x = x
        self.gap = self.GAP
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.set_height()

        self.passed = False

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height-self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)



        if t_point or b_point:
            return True
        return False



class Base:
    VEL = GAME_SPEED
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH <0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))







def draw_display(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)


    text = SCORE_FONT.render("Score: " + str(score), 1, (255, 255, 0))
    win.blit(text, (DISPLAY_WIDTH - 10 - text.get_width(), 10))
    text1 = SCORE_FONT.render("Generation: " + str(gen), 1, (255, 205, 0))
    win.blit(text1, (DISPLAY_WIDTH - 10 - text1.get_width(), 50))
    for bird in birds:
         bird.draw(win)

    base.draw(win)
    pygame.display.update()


def main(genomes, config):
    global gen
    gen+=1
    nets = []
    ge = []
    birds = []


    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)


    base = Base(BASE_HEIGHT)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0
    add_pipe = False
    while run:
        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_int = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_int = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_int].height), abs(bird.y - pipes[pipe_int].bottom)))

            if output[0] > 0.5:
                bird.jump()


        add_pipe = False
        remove_pipe = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                  #  print("yayayyhchjdhbscj................................\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                   # print("yayayyhchjdhbscj................................")

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

            pipe.move()

        if add_pipe:
            score+=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in remove_pipe:
            pipes.remove(r)
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= BASE_HEIGHT or bird.y < 0:
                ge[x].fitness -= 2
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        draw_display(win, birds, pipes, base, score, gen)
        base.move()





def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
    print(winner)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat.txt")
    run(config_path)



