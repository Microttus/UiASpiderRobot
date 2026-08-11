import time

class Leg:
    def __init__(self, bus, coxa_id, femur_id, tibia_id):
        self.coxa = bus.get_servo(coxa_id)
        self.femur = bus.get_servo(femur_id)
        self.tibia = bus.get_servo(tibia_id)

    def prepare_all(self, coxa_pos, femur_pos, tibia_pos, move_time):
        self.coxa.move_time_wait_write(coxa_pos, move_time)
        self.femur.move_time_wait_write(femur_pos, move_time)
        self.tibia.move_time_wait_write(tibia_pos, move_time)

    def prepare_coxa(self, coxa_pos, move_time):
        self.coxa.move_time_wait_write(coxa_pos, move_time)

    def prepare_femur(self, femur_pos, move_time):
        self.femur.move_time_wait_write(femur_pos, move_time)

    def prepare_tibia(self, tibia_pos, move_time):
        self.tibia.move_time_wait_write(tibia_pos, move_time)
    
    def set_pos(self, coxa, femur, tibia=500, move_time=1.5):
        self.prepare_all(coxa, femur, tibia, move_time)

    def read_coxa(self): #Lese posisjon
        return self.coxa.pos_read()
    def read_femur(self):
        return self.femur.pos_read()
    def read_tibia(self):
        return self.tibia.pos_read()
    
    def sitt(self):
        self.prepare_coxa(500, 5)
        self.prepare_femur(300, 5)
        self.prepare_tibia(200, 5)

    
    #Stå opp
    def start1(self):
        self.prepare_coxa(500,1)
        self.prepare_femur(225,5)
        self.prepare_tibia(160,5)

    def start2(self):
        self.prepare_all(500, 500, 400, 5)

    #Jævlig høy!
    def High(self):
        self.prepare_femur(700,5)
        self.prepare_tibia(600,5)
        

    #SixSeven
    def SixSevenV1(self):
        self.prepare_coxa(300,0.1)
        self.prepare_femur(300,0.1)
        self.prepare_tibia(600,1)
    
    def SixSevenV2(self):
        self.prepare_coxa(300,0.1)
        self.prepare_femur(200,0.1)
        self.prepare_tibia(600,1)

    def SixSevenH1(self):
        self.prepare_coxa(700,0.1)
        self.prepare_femur(200,0.1)
        self.prepare_tibia(600,1)
    
    def SixSevenH2(self):
        self.prepare_coxa(700,0.1)
        self.prepare_femur(300,0.1)
        self.prepare_tibia(600,1)


    #Altererende tetrapod-gange

    def fremover_gange_start(self, leg_index):
    # Bein 1, 4, 5, 8
        if leg_index in {0, 3, 4, 7}:
            self.start2()

    # Bein 2, 7
        elif leg_index in {1, 6}:
            self.Pos4()

    # Bein 3, 6
        elif leg_index in {2, 5}:
            self.Pos3()
    
    def HPos1(self):
        self.prepare_coxa(500,0.5)
        self.prepare_femur(400,0.01)
        self.prepare_tibia(400,1)
    
    def HPos2(self):
        self.prepare_coxa(500,0.5)
        self.prepare_femur(500,0.5)
        self.prepare_tibia(400,0.5)

    def HPos3(self):
        self.prepare_coxa(396,0.5)
        self.prepare_femur(500,0.5)
        self.prepare_tibia(400,0.5)
 
    def HPos4(self):
        self.prepare_coxa(604,0.5)
        self.prepare_femur(500,0.5)
        self.prepare_tibia(400,0.5)
    
    #Bein1: 1-4-2-3-1-4-2-3
    #Bein4: 2-3-1-4-2-3-1-4
    #Bein5: 1-3-2-4-1-3-2-4
    #Bein8: 2-4-1-3-2-4-1-3
    
    def Pos3(self):
        self.prepare_coxa(458,0.5)
        self.prepare_femur(500,0.5)
        self.prepare_tibia(400,0.5)

    def Pos4(self):
        self.prepare_coxa(542,0.5)
        self.prepare_femur(500,0.5)
        self.prepare_tibia(400,0.5)

    #Bein2: 4-2-3-1-4-2-3-1
    #Bein3: 3-1-4-2-3-1-4-2
    #Bein6: 3-2-4-1-3-2-4-1
    #Bein7: 4-1-3-2-4-1-3-2
  


        
