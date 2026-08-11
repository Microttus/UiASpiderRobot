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

    def read_coxa(self): #Lese posisjon
        return self.coxa.pos_read()
    def read_femur(self):
        return self.femur.pos_read()
    def read_tibia(self):
        return self.tibia.pos_read()
    
    def sitt(self):
        self.prepare_coxa(500, 1)
        self.prepare_femur(300, 10)
        self.prepare_tibia(500, 10)

    def start1(self):
        self.prepare_coxa(500,1)
        self.prepare_femur(225,5)
        self.prepare_tibia(160,5)

    def start2(self):
        self.prepare_femur(500,1)
        self.prepare_tibia(500,1)

    def SixSeven1(self):
        self.prepare_femur(100,1)

    def SixSeven2(self):
        self.prepare_femur(400,1)


    #Altererende tetrapod-gange

    def Bein1(self):
        self.prepare_coxa(500,1)
        self.prepare_femur(225,5)
        self.prepare_tibia(160,5)


        
