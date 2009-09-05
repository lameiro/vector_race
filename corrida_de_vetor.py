import pygraph
import math
import Image, ImageDraw

WIDTH  = 64
HEIGHT = 32
#WIDTH  = 8
#HEIGHT = 8
SQUARE_SIZE = 16

SPEED_TO_COLOR = [(255, 200, 200), (255, 150, 150), (255, 100, 100), (255, 50, 50), (255, 0, 0)]

GRASS_COLOR = (0,255,0)
TRACK_COLOR = (0,0,0)

class Node:
    def __init__(self, x_pos, y_pos, x_speed, y_speed):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_speed = x_speed
        self.y_speed = y_speed
        
    def speed(self):
        return math.sqrt(self.x_speed**2 + self.y_speed**2)
        
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x_pos == other.x_pos and self.y_pos == other.y_pos and self.x_speed == other.x_speed and self.y_speed == other.y_speed
        else:
            return False
    
    def __hash__(self):
        return self.x_pos*1000 + self.y_pos*100 + self.x_speed*10 + self.y_speed
    
    def __gt__(self, other):
        if self.x_pos != other.x_pos:
            return self.x_pos > other.x_pos
        else:
            return self.y_pos > other.y_pos
    
    def __str__(self):
        return 'x_pos = %d, y_pos = %d, x_speed = %d, y_speed = %d' % (self.x_pos, self.y_pos, self.x_speed, self.y_speed)
    
    __repr__ = __str__

def node_on_track(node):
    if 0 <= node.x_pos < WIDTH and 0 <= node.y_pos < HEIGHT:
        return track[node.y_pos][node.x_pos] == '.'
    else:
        return False
        
def process_node(node):
    for accel_x in range(-1, 2):
        for accel_y in range(-1, 2):
            possible_node = Node(node.x_pos + node.x_speed + accel_x, node.y_pos + node.y_speed + accel_y, node.x_speed + accel_x, node.y_speed + accel_y)
            if node_on_track(possible_node):
                yield possible_node
    
    
track = open(r'track.txt').readlines()

root_node   = Node(0,0,0,0)
target_node = Node(63,0,0,0)

graph = pygraph.digraph()
graph.add_node(root_node)
nodes_to_process = [root_node]

vertex_count = 0
edge_count = 0

found_target_node = False
index = 0

try:
    while not found_target_node:
        current_node = nodes_to_process[index]
        nodes_to_add = process_node(current_node)
        #print "Processing of node %s generated %s" % (current_node, nodes_to_add)
        
        for node_to_add in nodes_to_add:
            if node_to_add not in graph:
                graph.add_node(node_to_add)
                vertex_count += 1
                nodes_to_process.append(node_to_add)
            graph.add_edge(current_node, node_to_add)
            edge_count += 1
            if node_to_add == target_node:
                found_target_node = True
                break
        
        index += 1
        
        if index % 250 == 0:
            print '%d nodes processed.' % index
except IndexError:    
    largest_x = max(nodes_to_process, key=lambda node:node.x_pos)
    largest_y = max(nodes_to_process, key=lambda node:node.y_pos)
    
    print largest_x, largest_y

print 'Vertex count = %d, edge count = %d' % (vertex_count, edge_count)
print 'Now searching the target node...'
shortest_path_dict = pygraph.algorithms.searching.breadth_first_search(graph, root_node)[0]
print 'Calculation done. Printing shortest path and speeds'


shortest_path = [target_node]
while target_node != root_node:
    target_node = shortest_path_dict[target_node]
    shortest_path.append(target_node)
    
shortest_path.reverse()


im = Image.new('RGBA', (16*WIDTH, 16*HEIGHT))
d = ImageDraw.Draw(im)

for i in range(WIDTH):
    for j in range(HEIGHT):
        n = Node(i, j, 0, 0)
        if node_on_track(n):
            color = TRACK_COLOR
        else:
            color = GRASS_COLOR
        d.rectangle(((SQUARE_SIZE*i, SQUARE_SIZE*j), (SQUARE_SIZE*(i+1), SQUARE_SIZE*(j+1))), fill=color)

speed_sum = 0
for node in shortest_path:
    speed = node.speed()
    print (node, speed)
    speed_sum += speed
    color = SPEED_TO_COLOR[int(speed)]
    d.rectangle(((SQUARE_SIZE*node.x_pos, SQUARE_SIZE*node.y_pos), (SQUARE_SIZE*(node.x_pos+1), SQUARE_SIZE*(node.y_pos+1))), fill=color)
    
for i, node in enumerate(shortest_path):
    if i+1 < len(shortest_path):
        next_node = shortest_path[i+1]
        d.line(((SQUARE_SIZE*node.x_pos + SQUARE_SIZE/2, SQUARE_SIZE*node.y_pos + SQUARE_SIZE/2), (SQUARE_SIZE*next_node.x_pos + SQUARE_SIZE/2, SQUARE_SIZE*next_node.y_pos+SQUARE_SIZE/2)), width=4)
    
im.save('track.png', "PNG")
print 'Average speed = %f' % (1.0*speed_sum/len(shortest_path))