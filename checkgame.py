import pygame
import sys

class Pieces:
    #Represents all game pieces on board
    
    def __init__(self):
        self.graph=self.graph_representation()
        self.locations=[[None]*8 for _ in range(8)]
        row_count=-1

        for row in self.locations: 
            col_count=-1
            row_count+=1
            for column in row:
                col_count+=1

                #light squares when row is even and column is even  or when both odd
                if ((row_count%2==0 and col_count%2==0) or (row_count%2==1 and col_count%2==1)):
                    self.locations[row_count][col_count]=''
                else:
                    #Top rows are blk pieces
                    if(row_count<=2):
                        #create black PIECE in right location
                        piece=Piece('blk',col_count,row_count)

                        #instead of string set index of array to piece
                        self.locations[row_count][col_count]=piece

                    #middle rows blank
                    elif(row_count>2 and row_count<5):
                        self.locations[row_count][col_count]=''

                    #bottom rows are red pieces
                    elif(row_count>=5):
                        #create red PIECE in right location
                        piece=Piece('red',col_count,row_count)

                        #instead of string set index of array to piece
                        self.locations[row_count][col_count]=piece
        
    def draw_pieces(self):

        global SELECTED
        #self.locations is an 8x8 array showing where pieces are on board
        for row in self.locations:
            for piece in row:
                #if piece='' means spot is empty so continue onto next index
                if piece=='':
                    continue
                #draw piece based on location and colour
                elif piece.color=='red':
                    game_piece=piece.rect
                    #If piece is selected to be moved highlight green
                    if SELECTED==piece.rect:

                        pygame.draw.ellipse(screen,pygame.color.Color('green'),game_piece)
                    
                    #If red piece is king, change colour to gold
                    elif piece.king_status==True:
                        pygame.draw.ellipse(screen,gold,game_piece)

                    else:
                        pygame.draw.ellipse(screen,burnt_red,game_piece)

                elif piece.color=='blk':
                    game_piece=piece.rect
                    #If piece is selected to be moved highlight green
                    if SELECTED==piece.rect:
                        pygame.draw.ellipse(screen,pygame.color.Color('green'),game_piece)

                    #If blk piece is king, change colour to grey
                    elif piece.king_status==True:
                        pygame.draw.ellipse(screen,grey,game_piece)
                        
                    else:
                        pygame.draw.ellipse(screen,black,game_piece)

    def make_move(self):
        global SELECTED,TURN 

        if TURN%2==1: 
            color_to_play='blk' 
        else:
            color_to_play='red'
        #check if left click was pressed
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            #get coords of left click (either going to be pos of game piece to move or desired pos)
            pos=event.pos
            pos_x,pos_y=pos  #collect x and y coords of pos 
            pos_x=pos_x//75
            pos_y=pos_y//75

            for row in self.locations:
                for piece in row:
                    #if piece is alreaady selected
                    if piece!='' and SELECTED==piece.rect and piece.color==color_to_play:

                        if piece.can_move(self, pos_x, pos_y):
                            piece.move(self,pos_x, pos_y)
                            
                            SELECTED=None
                            TURN+=1
                            return
                        else: #check if position is result of multijump and if can do it
                            mod=pos_x%2
                            if pos_y%2==mod:
                                break
                            if pos_x==piece.x_pos and pos_y==piece.y_pos:
                                break
                            all_paths=[]
                            path=[]
                            visited={}
                            for position in self.graph:
                                visited[position]=False
                            list_paths=self.find_all_paths((piece.x_pos,piece.y_pos),(pos_x,pos_y),visited,path,all_paths)
                            
                            if len(list_paths)!=0:
                                #check if can do any of these multijumps
                                for list_moves in list_paths:
                                    if piece.can_move_sequence(self,list_moves):
                                        #take all moves and break
                                        for position in list_moves[1:]: #index 0 is current position cant move to current position
                                            piece.move(self,position[0],position[1])
                                        
                                        SELECTED=None
                                        TURN+=1
                                        return
                        
                    
                    #check if a piece is clicked on           
                    if piece!='' and piece.rect.collidepoint(pos) and piece.color==color_to_play:
                        #if piece is selected highlight green
                        SELECTED=piece.rect
                    
    def wincheck(self):
        blk_count=0
        red_count=0
        for row in self.locations:
            for col in row:
                if col!='' and col.color=='red':
                    red_count+=1
                elif col!='' and col.color=='blk':
                    blk_count+=1
        if red_count==0:
            #create surface for text
            blk_win_text =game_font.render("BLACK WINS!!",False,(255,255,255))
            screen.blit(blk_win_text,(190,300))#puts text surface on screen
        
        elif blk_count==0:
            #create surface for text
            red_win_text =game_font.render("RED WINS!!",False,(255,255,255))
            screen.blit(red_win_text,(190,300))#puts text surface on screen

    def freedom_check(self):
        free_reds=0
        free_blks=0
        #check freedom of reds
        for row in self.locations:
                for piece in row:
                    #check if piece is free
                    if piece!='' and piece.color=='red':
                        
                        #if spot diagonal and up and right is clear the piece is free and piece not in right most column nor in 1st row 
                        if piece.x_pos!=7 and piece.y_pos>0 and self.locations[piece.y_pos-1][piece.x_pos+1]=='':
                            free_reds+=1
                            continue
                                
                        #if spot diagonal and up and left is clear the piece is free and piece not in left most column
                        elif piece.x_pos!=0 and piece.y_pos>0 and self.locations[piece.y_pos-1][piece.x_pos-1]=='':
                            free_reds+=1
                            continue
          
                        if piece.king_status==True:
                            #if spot diagonal and down and right is clear the piece is free and piece not in right most column nor in first row
                            if piece.x_pos!=7 and piece.y_pos<7 and self.locations[piece.y_pos+1][piece.x_pos+1]=='':
                                free_reds+=1
                                continue
                                
                            #if spot diagonal and down and left is clear the piece is free and piece not in left most column
                            elif piece.x_pos!=0 and piece.y_pos<7 and self.locations[piece.y_pos+1][piece.x_pos-1]=='':
                                free_reds+=1
                                continue

                        #checks if red can eat piece
                        for neighbor in self.graph[(piece.x_pos,piece.y_pos)]:
                            if piece.can_move(self,neighbor[0],neighbor[1]):
                                free_reds+=1
                                break
                        continue
                        

                    elif piece!='' and piece.color=='blk':
                        
                        #if spot diagonal and down and right is clear the piece is free and piece not in right most column nor in last row
                        if piece.x_pos<7 and piece.y_pos<7 and self.locations[piece.y_pos+1][piece.x_pos+1]=='':
                            free_blks+=1
                            continue
                                
                        #if spot diagonal and down and left is clear the piece is free and piece not in left most column nor in last row
                        elif piece.x_pos!=0 and piece.y_pos<7 and self.locations[piece.y_pos+1][piece.x_pos-1]=='':
                            free_blks+=1
                            continue
                        
                        if piece.king_status==True:
                            #if spot diagonal and up and right is clear  and piece not in right most column  the piece is free
                            if piece.x_pos!=7 and self.locations[piece.y_pos-1][piece.x_pos+1]=='':
                                free_blks+=1
                                continue
                                
                            #if spot diagonal and up and left is clear  and piece not in left most column the piece is free
                            elif piece.x_pos!=0 and self.locations[piece.y_pos-1][piece.x_pos-1]=='':
                                free_blks+=1
                                continue

                        #checks if blk can eat piece
                        for neighbor in self.graph[(piece.x_pos,piece.y_pos)]:
                            if piece.can_move(self,neighbor[0],neighbor[1]):
                                free_blks+=1
                                break
                        continue
                       
        if free_blks==0:
            #create surface for text
            blk_win_text =game_font.render("RED WINS!!",False,(255,255,255))
            screen.blit(blk_win_text,(190,300))#puts text surface on screen
        
        elif free_reds==0:
            #create surface for text
            red_win_text =game_font.render("BLACK WINS!!",False,(255,255,255))
            screen.blit(red_win_text,(190,300))#puts text surface on screen

    def graph_representation(self): #put this in init
        #this method will help implement double jumps
        # represent board as graph with neighbors being 2 places away diagonally
        #using adjacency representation
        graph={}
        
        for row_count in range(8):
             for col_count in range(8):
                 #if one odd and one even it is a valid playing position
                 if (row_count%2==0 and col_count%2==1) or (row_count%2==1 and col_count%2==0):
                    #add it to the dictionary along with its neighbors 2 places away diagonally
                    graph[(col_count,row_count)]=[]
                    #adjacency list is list of tuples of positions neighboring by 2
                    
                    #row_count is y axis, col_count is x axis

                    #uright neighbor
                    if(row_count-2 >= 0) and (col_count+2 <=7):
                        graph[(col_count,row_count)].append((col_count+2,row_count-2))

                    #uleft neighbor
                    if(row_count-2 >= 0) and (col_count-2 >=0):
                        graph[(col_count,row_count)].append((col_count-2,row_count-2))
                    #dright neighbor 
                    if(row_count+2 <= 7) and (col_count+2 <=7):
                        graph[(col_count,row_count)].append((col_count+2,row_count+2))
                    #dleft neighbor
                    if(row_count+2 <= 7) and (col_count-2 >=0):
                        graph[(col_count,row_count)].append((col_count-2,row_count+2))
        return graph

    def find_all_paths(self,start,destination,visited,path,all_paths):
        #start is starting position as tuple, destination of same form
        #path is list of tuples 
        #visited is a dictionary holding all playable board positions and whether they have been visited
        #important fact about multi: always going to be jumping by 2


        #visit position and add it to the path
        visited[start]=True
        path.append(start)       

        #if cur position is same as destination
        #add path to all paths list (list of lists of tuples)  
        if start==destination:
            #deepcopy path 
            #since path is added to all paths, pop method would alter the paths in all paths, thats why we need deepcopy
            path_save=[]
            for position in path:
                path_save.append(position)
            all_paths.append(path_save) 

        else: 
            # If cur position not destination 
            # visit all positions 2 spaces diagonally from this position (neighbors)
            for neighbor in self.graph[start]: 
                if visited[neighbor]== False: 
                    self.find_all_paths(neighbor, destination, visited, path,all_paths)      

        #if current position is destination or has no more unvisited neighbors
        #remove current position from path and mark as unvisited
        path.pop()
        visited[start]=False

        return all_paths
         
                                          
class Piece:
    #Represents single piece
    def __init__(self,color,x_pos,y_pos,king_status=False):
        self.color=color
        self.x_pos=x_pos
        self.y_pos=y_pos
        self.king_status=king_status
        self.rect = pygame.Rect(self.x_pos*75+10,self.y_pos*75+15,50,50)

    #def can_eat(self): global TURN, SELECTED
    #def eat(self)    global TURN, SELECTED
    def can_move(self,play_board,pos_x,pos_y):
        #returns true or false 
        mod=pos_x%2
        if pos_y%2==mod:
            return False
        if pos_x==self.x_pos and pos_y==self.y_pos:
            return False

        if self.color=='red' or self.king_status==True: 

            #if going up and right: (can only do this if king or red piece)
            #play_board.locations checking if place to move to is free
            if pos_x-1== self.x_pos and pos_y+1 ==self.y_pos and play_board.locations[self.y_pos-1][self.x_pos+1]=='': 
                return True

            #if going up and right and want to eat opponent (have to be king or red piece)
            elif pos_x-2==self.x_pos and pos_y+2==self.y_pos:
                #!=self.color makes sure you aare eating oppostie team piece
                if play_board.locations[self.y_pos-1][self.x_pos+1]!='' and play_board.locations[self.y_pos-2][self.x_pos+2]=='' and play_board.locations[self.y_pos-1][self.x_pos+1].color!=self.color: 
                    return True

            #if going up and left: can only do this if king or red piece
            elif pos_x+1== self.x_pos and pos_y+1 ==self.y_pos and play_board.locations[self.y_pos-1][self.x_pos-1]=='':
                return True

            elif pos_x+2==self.x_pos and pos_y+2==self.y_pos:

                #check if inbetween current position and desired position is enemy piece and that desired position is free
                if play_board.locations[self.y_pos-1][self.x_pos-1]!='' and play_board.locations[self.y_pos-2][self.x_pos-2]=='' and play_board.locations[self.y_pos-1][self.x_pos-1].color!=self.color: 
                    return True
        
        if self.color=='blk' or self.king_status==True:

            #if going down and right: king or black
            if pos_x-1== self.x_pos and pos_y-1 ==self.y_pos and play_board.locations[self.y_pos+1][self.x_pos+1]=='':
                return True

            #if going down and right and want to eat opponent: king or black
            elif pos_x-2==self.x_pos and pos_y-2==self.y_pos:
                #check if inbetween current position and desired position is enemy piece and that desired position is free
                if play_board.locations[self.y_pos+1][self.x_pos+1]!='' and play_board.locations[self.y_pos+2][self.x_pos+2]=='' and play_board.locations[self.y_pos+1][self.x_pos+1].color!=self.color:
                    return True

            #if going down and left: king or blk
            elif pos_x+1== self.x_pos and pos_y-1 ==self.y_pos and play_board.locations[self.y_pos+1][self.x_pos-1]=='':
                return True

            #if going down and left and want to eat opponent: king or blk
            elif pos_x+2==self.x_pos and pos_y-2==self.y_pos:

                #check if inbetween current position and desired position is enemy piece and that desired position is free
                if play_board.locations[self.y_pos+1][self.x_pos-1]!='' and play_board.locations[self.y_pos+2][self.x_pos-2]=='' and play_board.locations[self.y_pos+1][self.x_pos-1].color!=self.color: 
                    return True

        return False
      
    def move(self,play_board,pos_x,pos_y):  #  eats piece in way if have to, pos must be either diagonal 1 or 2 spaces away.
        global TURN, SELECTED #do this in move_piece method

        #if self.can_move(play_board,pos_x,pos_y): function only used when this true
            #if can move to position move there

        #if 1 slot away just move
        if (pos_x-self.x_pos)%2==1 and (pos_y-self.y_pos)%2==1:
            move_x=(pos_x-self.x_pos) * 75
            move_y=(pos_y-self.y_pos) *75
            self.rect.move_ip(move_x,move_y)

            #remove piece from old position
            play_board.locations[self.y_pos][self.x_pos]=''
            #update x_pos and y_pos
            self.x_pos+=(pos_x-self.x_pos)
            self.y_pos+=(pos_y-self.y_pos)

            #Checking if to update red piece to king
            if self.y_pos==0 and self.king_status==False and self.color=='red':
                self.king_status=True
            
            #Checking if to update blk piece to king
            if self.y_pos==7 and self.king_status==False and self.color=='blk':
                self.king_status=True

            #update play_board.locations (y.pos==row_count in play_board.locations and x.pos ==col_count)
            play_board.locations[self.y_pos][self.x_pos]=self


        #if 2 slots away eat and move
        elif (pos_x-self.x_pos)%2==0 and (pos_y-self.y_pos)%2==0:
            move_x=(pos_x-self.x_pos) * 75
            move_y=(pos_y-self.y_pos) *75
            self.rect.move_ip(move_x,move_y)

            #remove piece from old position
            play_board.locations[self.y_pos][self.x_pos]=''

            #remove enemy piece from old position i.e destroy enemy piece
            play_board.locations[self.y_pos+(pos_y-self.y_pos)//2][self.x_pos+(pos_x-self.x_pos)//2]=''


            #update x_pos and y_pos
            self.x_pos+=(pos_x-self.x_pos)
            self.y_pos+=(pos_y-self.y_pos)

            #Checking if to update red piece to king
            if self.y_pos==0 and self.king_status==False and self.color=='red':
                self.king_status=True
            
            #Checking if to update blk piece to king
            if self.y_pos==7 and self.king_status==False and self.color=='blk':
                self.king_status=True

            #update play_board.locations (y.pos==row_count in play_board.locations and x.pos ==col_count)
            play_board.locations[self.y_pos][self.x_pos]=self

                
    
    def can_move_sequence(self,play_board,list_moves):
        #used for multijumps, all consecutive positions in list_moves are 2 positions away from each other
        #list_moves is a list of tuples// tuples are locations on board
    
        #check if possible to perform all of the moves in list
        #make dummy piece to see if moves possible
        dummyPiece= Piece(self.color,self.x_pos,self.y_pos,self.king_status) 
        #first position in path is current position so start from second index
        for pos in list_moves[1:]:
            if dummyPiece.can_move(play_board,pos[0],pos[1]):
                dummyPiece.x_pos=pos[0]
                dummyPiece.y_pos=pos[1]
            else:
                return False
        return True
        


def draw_board():
    check_board=[[None]*8 for _ in range(8)]
    row_count=-1

    for row in check_board:
        col_count=-1
        row_count+=1
        for column in row:
            col_count+=1
            square = pygame.Rect(col_count*75,row_count*75,75,75)

            #place rect in array
            check_board[row_count][col_count]=square

            #light squares when row is even and column is even  or when both odd
            if ((row_count%2==0 and col_count%2==0) or (row_count%2==1 and col_count%2==1)):
                pygame.draw.rect(screen,light_brown,square)
            else:
                pygame.draw.rect(screen,dark_brown,square)

    return check_board
            
#general setup
pygame.init()
clock=pygame.time.Clock()

bg_color=(29,181,101) #light green
dark_brown=(115,64,18)
light_brown=(224,139,62)
black=(0,0,0)
burnt_red=(153,26,0)
grey=(105,105,105)
gold=(255,215,0)

#setup main window
screen_width=600
screen_height=600
screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Checkm8')

#game variables
START_BUTTON=pygame.Rect(255,250,84,30)
start_font=pygame.font.Font("freesansbold.ttf",32)
CLICK=False

#keep track of currently selected game piece
SELECTED = None


#Text Variables
game_font=pygame.font.Font("freesansbold.ttf",32)


#GAME LOOP
while True:
    #displaying start button
    pygame.draw.rect(screen,burnt_red,START_BUTTON)
    
    screen.fill(bg_color)
    draw_board()

    #get position of mouse
    mouse_x,mouse_y=pygame.mouse.get_pos()

    

    start_text = start_font.render("PLAY",False,gold)
    screen.blit(start_text,(255,250))#puts text surface on screen

    #checking if clicked start button
    if START_BUTTON.collidepoint((mouse_x,mouse_y)):
        if CLICK:
            TURN=1
            hello=Pieces()
            running=True
            while running: 

                screen.fill(bg_color)

                for event in pygame.event.get():
                    if event.type==pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type==pygame.KEYDOWN:
                        if event.key==pygame.K_ESCAPE:
                            running=False
    
                    hello.make_move()    
                                       
                #visuals
                draw_board()
                hello.draw_pieces()
                hello.wincheck()
                hello.freedom_check()

                #updating window
                pygame.display.flip()
                clock.tick(60)

    CLICK=False

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                CLICK=True
        
                
    #updating window
    pygame.display.flip()
    clock.tick(60)

