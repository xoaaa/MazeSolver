import pygame
import random
import sys


BACKGROUND_COLOR = (255,192,203)
GRID_LINE_COLOR = (50,50,80)
GRID_LINE_THICKNESS = 2 

try:
    TILE_SIZE = 40  
    WALL_TEXTURE = pygame.image.load("assets/batu.png")
    WALL_TEXTURE = pygame.transform.scale(WALL_TEXTURE, (TILE_SIZE, TILE_SIZE))
except:
    WALL_TEXTURE = None  

def scene_main_menu():
    screen = pygame.display.set_mode((800,800))
    pygame.display.set_caption("Maze Solver - Main Menu")

    bg = pygame.image.load("assets/main.png")
    start = pygame.image.load("assets/start.png")
    quitb = pygame.image.load("assets/quit.png")

    bg = pygame.transform.scale(bg, (800,800))
    start = pygame.transform.scale(start, (220,80))
    quitb = pygame.transform.scale(quitb, (220,80))

    start_rect = start.get_rect(center=(400,450))
    quit_rect = quitb.get_rect(center=(400,550))

    while True:
        screen.blit(bg,(0,0))
        screen.blit(start,start_rect)
        screen.blit(quitb,quit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(pygame.mouse.get_pos()):
                    return "SCENE_INTRO"
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit(); sys.exit()

        pygame.display.flip()


def scene_intro():
    screen = pygame.display.set_mode((800,800))
    pygame.display.set_caption("Maze Solver - Introduction")

    bg = pygame.image.load("assets/intro.png")
    cont = pygame.image.load("assets/continue.png")
    bg = pygame.transform.scale(bg, (800,800))
    cont = pygame.transform.scale(cont, (220,80))
    cont_rect = cont.get_rect(center=(400,650))

    while True:
        screen.blit(bg,(0,0))
        screen.blit(cont,cont_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cont_rect.collidepoint(pygame.mouse.get_pos()):
                    return "SCENE_TUTORIAL"

        pygame.display.flip()


def scene_tutorial():
    screen = pygame.display.set_mode((800,800))
    pygame.display.set_caption("Maze Solver - Tutorial")

    bg = pygame.image.load("assets/tutorial.png")   
    cont = pygame.image.load("assets/continue.png")

    bg = pygame.transform.scale(bg, (800,800))
    cont = pygame.transform.scale(cont, (220,80))
    cont_rect = cont.get_rect(center=(400,700))

    while True:
        screen.blit(bg,(0,0))
        screen.blit(cont,cont_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cont_rect.collidepoint(pygame.mouse.get_pos()):
                    return "SCENE_GAME"

        pygame.display.flip()

class CoOrdinates():
    def __init__(self):
        self.remove_all()

    def remove_all(self):
        self.start = None
        self.end = None
        self.walls = []
        self.maze = []
        self.open_list = []
        self.closed_list = []
        self.final_path = []
        self.check_points = []

    def remove_last(self):
        self.maze = []
        self.open_list = []
        self.closed_list = []
        self.final_path = []

    def largest_distance(self):
        largest = 0
        for wall in self.walls:
            largest = max(largest, wall[0], wall[1])
        for point in self.check_points:
            if point != "None":  # skip invalid
                largest = max(largest, point[0], point[1])
        return largest + 1
    
    def create_maze(self, gui):
        largest_distance = self.largest_distance()
        largest = max(gui.grid_size, largest_distance)
        self.maze = [[0 for x in range(largest)] for y in range(largest)]
        for wall in self.walls:
            x,y = wall
            self.maze[x][y] = 1

    def generate_random_maze(self, gui):
        self.walls = []
        for i in range(gui.grid_size * gui.grid_size):
            if random.random() > 0.6:
                wall = (random.randint(0, gui.grid_size-1), random.randint(0, gui.grid_size-1))
                if wall not in self.walls:
                    self.walls.append(wall)


class Gui():
    FPS = 60
    WIDTH = 800
    
    def __init__(self, coords):
        self.grid_size = 20
        self.box_width = self.WIDTH/self.grid_size
        self.coords = coords
        self.placing_walls = False
        self.removing_walls = False
        self.animation_speed = 10
        self.coords.maze = [[0 for x in range(self.grid_size)] for y in range(self.grid_size)]

        pygame.display.set_caption("Maze Solver - Pathfinding")
        self.win = pygame.display.set_mode((self.WIDTH, self.WIDTH))
        self.clock = pygame.time.Clock()

    def main(self, running=False):
        self.clock.tick(self.FPS)
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        if not running:
            if self.placing_walls: self.place_wall()
            elif self.removing_walls: self.remove()

        self.event_handle(running)
        self.redraw()
        pygame.display.update()

    def event_handle(self, running):
        run_keys = {"q","w","e","r"}
        checkpoint_keys = {"1","2","3","4","5","6","7","8","9"}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)

                if not running:
                    if key in run_keys:
                        self.run_algorithm(key)
                    elif key=="x":
                        self.coords.remove_all()
                    elif key=="z":
                        self.coords.remove_last()
                    elif key in checkpoint_keys:
                        self.place_check_point(key)

                elif (key in ["+","="]) and self.animation_speed>0:
                    self.animation_speed = 1 if self.animation_speed<=2 else int(self.animation_speed*0.5)+1
                elif key=="-":
                    self.animation_speed = int(self.animation_speed*2)+1
                elif key==" ":
                    self.coords.generate_random_maze(gui)

            elif event.type==pygame.MOUSEBUTTONDOWN:
                if not running:
                    if event.button==1: self.placing_walls=True
                    elif event.button==3: self.removing_walls=True
                if event.button==4:
                    self.grid_size-=1; self.box_width=self.WIDTH/self.grid_size
                elif event.button==5:
                    self.grid_size+=1; self.box_width=self.WIDTH/self.grid_size

            elif event.type==pygame.MOUSEBUTTONUP:
                if event.button==1: self.placing_walls=False
                elif event.button==3: self.removing_walls=False

    def redraw(self):
        self.win.fill(BACKGROUND_COLOR)
        self.draw_points()
        self.draw_grid()

    def draw_grid(self):
        for i in range(self.grid_size+1):
     
            pygame.draw.line(
                self.win, 
                GRID_LINE_COLOR, 
                (i * self.box_width, 0), 
                (i * self.box_width, self.WIDTH), 
                GRID_LINE_THICKNESS
            )
            pygame.draw.line(
                self.win, 
                GRID_LINE_COLOR, 
                (0, i * self.box_width), 
                (self.WIDTH, i * self.box_width), 
                GRID_LINE_THICKNESS
            )



    def draw_points(self):
        for node in self.coords.open_list: self.draw_box(node.position,(0,255,0))
        for node in self.coords.closed_list: self.draw_box(node.position,(0,0,255))
        for wall in self.coords.final_path: self.draw_box(wall,(255,0,255))

        for wall in self.coords.walls: self.draw_wall_texture(wall)

        for i,point in enumerate(self.coords.check_points):
            if point!="None":
                self.draw_box(point,(255,30,30))
                self.display_text(str(i+1),(255,255,255),self.box_center(point),int(self.box_width))

    def draw_wall_texture(self, box):
        x = box[0] * self.box_width
        y = box[1] * self.box_width

        if WALL_TEXTURE:
            texture = pygame.transform.scale(WALL_TEXTURE, (int(self.box_width), int(self.box_width)))
            self.win.blit(texture, (x, y))
        else:
            pygame.draw.rect(self.win, (0,0,0), (x, y, self.box_width, self.box_width))

    def box_center(self, b):
        return (b[0]*self.box_width+self.box_width/2, b[1]*self.box_width+self.box_width/2)

    def draw_box(self, box, color):
        pygame.draw.rect(self.win,color,(box[0]*self.box_width, box[1]*self.box_width, self.box_width, self.box_width))

    def get_box_coords(self):
        return (int((self.mouse_x+2)/self.box_width), int((self.mouse_y+2)/self.box_width))

    def place_check_point(self, index):
        coords = self.get_box_coords()
        if coords!=self.coords.start and coords!=self.coords.end and coords not in self.coords.walls and coords not in self.coords.check_points:
            while len(self.coords.check_points)<=int(index)-1:
                self.coords.check_points.append("None")
            self.coords.check_points[int(index)-1]=coords

    def place_wall(self):
        coords = self.get_box_coords()
        if coords!=self.coords.start and coords!=self.coords.end and coords not in self.coords.walls and coords not in self.coords.check_points:
            self.coords.walls.append(coords)

    def remove(self):
        coords = self.get_box_coords()
        if coords in self.coords.walls: self.coords.walls.remove(coords)
        elif coords in self.coords.check_points: self.coords.check_points.remove(coords)

    def run_algorithm(self, key):
        from math import sqrt
        self.placing_walls = False; self.removing_walls=False
        self.coords.remove_last()

        if len(self.coords.check_points)>1:
            self.coords.create_maze(gui)
            check_points = [c for c in self.coords.check_points if c!="None"]

            for i,point in enumerate(check_points):
                if i!=len(check_points)-1:
                    start=point; end=check_points[i+1]
                    new_path = pathfind(self.coords.maze,start,end,self,self.coords,key)
                    if new_path is None: new_path=[]
                    self.coords.final_path.extend(new_path)

    def display_text(self, txt, color, center, size):
        font = pygame.font.Font(None, size)
        surf = font.render(txt,True,color)
        rect = surf.get_rect(center=center)
        self.win.blit(surf,rect)


class Node:
    def __init__(self,parent,pos):
        self.parent=parent
        self.position=pos
        self.g=0;self.h=0;self.f=0

    def __eq__(self,other):
        return self.position==other.position


def pathfind(maze,start,end,gui,coords,key):
    start_node=Node(None,start); end_node=Node(None,end)
    open_list=[start_node]; closed_list=[]
    count=0

    while open_list:
        if count>=gui.animation_speed:
            count=0

            if key=="q": current_node=open_list[-1]
            elif key=="w": current_node=open_list[0]
            elif key=="e": current_node=min(open_list,key=lambda n:n.g)
            elif key=="r":
                current_node=min(open_list,key=lambda n:n.f)

            open_list.remove(current_node)
            closed_list.append(current_node)

            if current_node==end_node:
                path=[]; cur=current_node
                while cur: path.append(cur.position); cur=cur.parent
                coords.open_list=open_list; coords.closed_list=closed_list
                return path

            for move in [(-1,0),(0,1),(1,0),(0,-1)]:
                node_pos=(current_node.position[0]+move[0],current_node.position[1]+move[1])

                if node_pos[0]<0 or node_pos[0]>=len(maze) or node_pos[1]<0 or node_pos[1]>=len(maze):
                    continue
                if maze[node_pos[0]][node_pos[1]]!=0: continue
                if Node(current_node,node_pos) in closed_list: continue

                child=Node(current_node,node_pos)

                child.g=current_node.g+1
                if key=="r":
                    child.h=((abs(child.position[0]-end_node.position[0])**2)+(abs(child.position[1]-end_node.position[1])**2))**0.6
                    child.f=child.g+child.h

                if any(child==open_node and child.g>=open_node.g for open_node in open_list):
                    continue

                open_list.append(child)

        else:
            coords.open_list=open_list; coords.closed_list=closed_list
            gui.main(True)

        count+=1

pygame.init()

scene = "SCENE_MAIN"

while True:
    if scene == "SCENE_MAIN":
        scene = scene_main_menu()
    elif scene == "SCENE_INTRO":
        scene = scene_intro()
    elif scene == "SCENE_TUTORIAL":
        scene = scene_tutorial()
    elif scene == "SCENE_GAME":
        coords = CoOrdinates()
        gui = Gui(coords)
        while True:
            gui.main()
