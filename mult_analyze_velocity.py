import numpy as np 
import matplotlib.pyplot as plt
import getopt
import sys
import os.path
#--------------------------------------------------
def avg(x):
    return np.sum(x)/len(x)

def multi_avg(x,xerr):
    sum1 = 0
    sum2 = 0
    for i in range(len(x)):
        sum1 += x[i]/(xerr[i]**2)
        sum2 += 1/(xerr[i]**2)
    return sum1/sum2

def var(x):
    summ = 0 
    for i in x:
        summ += (i - avg(x))**2
    return summ/(len(x)-1)

def multi_var(xerr):
    summ = 0
    for i in range(len(xerr)):
        summ += 1/(xerr[i]**2)
    return np.sqrt(1/summ)

def make_varray(a,b):
    new = []
    for i in range(len(a)):
        new.append(a[i]+b[i])
    return new

def invert_sign(a):
    b = []
    for i in range(len(a)):
        b.append(-a[i])
    return b

def create_uncertainty(a,b):
    return make_varray(a,b),make_varray(a,invert_sign(b))

def remove_like(a):
    b=[]
    removed = 0
    for i in range(len(a)):
        if i>0:
            if a[i]==a[i-1]:
                #print('REMOVED {}'.format(a[i]))
                removed += 1
            else:
                b.append(a[i])
        else:
            b.append(a[i])
    return b

def find_time_elapsed(vel,start,stop):
    return (stop-start)/vel

def find_time_error(error,vel,start,stop):
    return np.sqrt((-(start-stop)*error/(vel**2))**2)

def find_mult_time_error(error,vel,start,stop):
    summate = 0
    for i in range(len(error)):
        summate += (-(stop-start)*error[i]/(vel[i]))**2
    return np.sqrt(summate)

#--------------------------------------------------
def process(parent,fileid):
    print(fileid)

    raw_time = []
    velocity = []
    torque = []
    pos_error = []
    pos = []

    read_file = open('{}/{}'.format(parent,fileid),'r')
    next(read_file)
    for line in read_file:
        line_seg = line.split(';')
        for i in range(4):
            line_inc = line_seg[i].split(' ')
            if i==0:
                raw_time.append(float(line_inc[0]))
                velocity.append(float(line_inc[1]))
            elif i==1:
                torque.append(float(line_inc[1]))
            elif i==2:
                pos_error.append(float(line_inc[1]))
            elif i==3:
                pos.append(float(line_inc[1]))
    
    
    ####   5 ms Parker Timing Interval: Multiply by 3.38!!!!    ###
    for i in range(len(raw_time)):
        raw_time[i] = raw_time[i]*3.3783783

    hole_open = -91875
    hole_close = -137601
    hole_center = -114288
    in_hole_index = []
    all_velocities = []
    useful_times = []
    in_hole = []
    in_hole_counter = []
    in_hole_clockw = []
    counter_vel = []
    clockw_vel = []
    counter_time = []
    clockw_time = []

    start_cntr_index = []
    start_clkw_index = []

    elapsed_time_cntr = []
    elapsed_time_clkw = []

    approach_hole_counter =[]
    approach_counter_vel = []
    approach_counter_time =[]
    approach_hole_clockw = []
    approach_clockw_vel = []
    approach_clockw_time =[]
    
    leave_hole_counter = []
    leave_counter_time = []
    leave_counter_vel =[]
    leave_hole_clockw = []
    leave_clockw_time = []
    leave_clockw_vel = []

    avg_before_hole_counter = []
    avg_after_hole_counter = []
    avg_before_hole_clockw = []
    avg_after_hole_clockw = []

    for i in range(len(pos)):
        if pos[i]>hole_close and pos[i]<hole_open:
            in_hole.append(pos[i])
            in_hole_index.append(i)
            if velocity[i]>0:
                in_hole_counter.append(pos[i])
                counter_time.append(raw_time[i])
                counter_vel.append(velocity[i])
                if pos[i]<hole_center:
                    for q in range(i,0,-1):
                        if abs(pos[q]+580000)<100:
                            start_cntr_index.append(q)
                            elapsed_time_cntr.append(raw_time[i]-raw_time[q])
                            break
                if pos[i-1]<hole_close:
                    approach_hole_counter.append(pos[i-1])
                    approach_counter_time.append(raw_time[i-1])
                    approach_counter_vel.append(velocity[i-1])
                if pos[i+1]>hole_open:
                    leave_hole_counter.append(pos[i+1])
                    leave_counter_time.append(raw_time[i+1])
                    leave_counter_vel.append(velocity[i+1])
            elif velocity[i]<0:
                in_hole_clockw.append(pos[i])
                clockw_time.append(raw_time[i])
                clockw_vel.append(velocity[i])
                if pos[i]>hole_center:
                    for q in range(i,0,-1):
                        if abs(pos[q]-350000)<100:
                            start_clkw_index.append(q)
                            elapsed_time_clkw.append(raw_time[i]-raw_time[q])
                            break
                if pos[i-1]>hole_open:
                    approach_hole_clockw.append(pos[i-1])
                    approach_clockw_time.append(raw_time[i-1])
                    approach_clockw_vel.append(velocity[i-1])
                if pos[i+1]<hole_close:
                    leave_hole_clockw.append(pos[i+1])
                    leave_clockw_time.append(raw_time[i+1])
                    leave_clockw_vel.append(velocity[i+1])


    start_cntr_index = remove_like(start_cntr_index)
    start_clkw_index = remove_like(start_clkw_index)

    indiv_time_thru_cntr = []
    for i in range(len(counter_vel)):
        indiv_time_thru_cntr.append(find_time_elapsed(counter_vel[i]*524288/60,hole_close,hole_open)*1000)

    indiv_time_thru_clkw = []
    for i in range(len(clockw_vel)):
        indiv_time_thru_clkw.append(find_time_elapsed(clockw_vel[i]*524288/60,hole_open,hole_close)*1000)


    avg_countr_v = [avg(counter_vel),var(counter_vel)]
    avg_clockw_v = [avg(clockw_vel),var(clockw_vel)]
    
    avg_elapsed_cntr = [avg(elapsed_time_cntr)*1000,var(elapsed_time_cntr)*1000]
    avg_elapsed_clkw = [avg(elapsed_time_clkw)*1000,var(elapsed_time_clkw)*1000]

    time_thru_countr = [find_time_elapsed(avg_countr_v[0]*524288/60,hole_close,hole_open)*1000,find_time_error(avg_countr_v[1]*524288/60,avg_countr_v[0]*524288/60,hole_close,hole_open)*1000]
    time_thru_clockw = [find_time_elapsed(avg_clockw_v[0]*524288/60,hole_open,hole_close)*1000,find_time_error(avg_clockw_v[1]*524288/60,avg_clockw_v[0]*524288/60,hole_close,hole_open)*1000]
    
    return counter_time,avg_countr_v,time_thru_countr,avg_elapsed_cntr,clockw_time,avg_clockw_v,time_thru_clockw,avg_elapsed_clkw,elapsed_time_cntr,elapsed_time_clkw,indiv_time_thru_cntr,indiv_time_thru_clkw

### ---------------------------------------------------- ###

def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:],'f:')
    except getopt.GetoptError as err:
        print(err)
    for o,a in opts:
        if o == '-f':
            directory = a
    
    print(directory)

    counter_velocity = []
    counter_vel_err = []
    counter_shutter_time = []
    counter_shutter_timeerr = []
    counter_time_from_start = []
    counter_time_starterr = []
    elapsed_counter = []
    time_thru_cntr = []

    clkw_velocity = []
    clkw_vel_err = []
    clkw_shutter_time = []
    clkw_shutter_timeerr = []
    clkw_time_from_start = []
    clkw_time_starterr = []
    elapsed_clockw = []
    time_thru_clkw = []


    list_size = 0
    data = []
    for root, dirs, files in os.walk(directory):
        for i in files:
            data.append(process(directory,i))

            counter_velocity.append(data[list_size][1][0])
            counter_vel_err.append(data[list_size][1][1])
            counter_shutter_time.append(data[list_size][2][0])
            counter_shutter_timeerr.append(data[list_size][2][1])
            counter_time_from_start.append(data[list_size][3][0])
            counter_time_starterr.append(data[list_size][3][1])
            for i in range(len(data[list_size][8])):
                elapsed_counter.append(data[list_size][8][i])
            for i in range(len(data[list_size][10])):
                time_thru_cntr.append(data[list_size][10][i])

            clkw_velocity.append(data[list_size][5][0])
            clkw_vel_err.append(data[list_size][5][1])
            clkw_shutter_time.append(data[list_size][6][0])
            clkw_shutter_timeerr.append(data[list_size][6][1])
            clkw_time_from_start.append(data[list_size][7][0])
            clkw_time_starterr.append(data[list_size][7][1])
            for i in range(len(data[list_size][9])):
                elapsed_clockw.append(data[list_size][9][i])
            for i in range(len(data[list_size][11])):
                time_thru_clkw.append(data[list_size][11][i])

            list_size += 1

    print('COUNTERCLOCKWISE:')
    print('Speed Through Shutter = {:.2f} +/- {:.2f} rpm'.format(multi_avg(counter_velocity,counter_vel_err),multi_var(counter_vel_err)))
    print('Time in Shutter = {:.2f} +/- {:.2f} ms'.format(multi_avg(counter_shutter_time,counter_shutter_timeerr),multi_var(counter_shutter_timeerr)))
    print('Time Since Start = {:.2f} +/- {:.2f} ms'.format(multi_avg(counter_time_from_start,counter_time_starterr),multi_var(counter_time_starterr)))
    print('CLOCKWISE:')
    print('Speed Through Shutter = {:.2f} +/- {:.2f} rpm'.format(multi_avg(clkw_velocity,clkw_vel_err),multi_var(clkw_vel_err)))
    print('Time in Shutter = {:.2f} +/- {:.2f} ms'.format(multi_avg(clkw_shutter_time,clkw_shutter_timeerr),multi_var(clkw_shutter_timeerr)))
    print('Time Since Start = {:.2f} +/- {:.2f} ms'.format(multi_avg(clkw_time_from_start,clkw_time_starterr),multi_var(clkw_time_starterr)))
  
    summ = 0 
    print(len(counter_time_from_start))
    for i in range(len(counter_time_from_start)):
        summ += ((counter_time_from_start[i]-multi_avg(counter_time_from_start,counter_time_starterr))**2)/multi_avg(counter_time_from_start,counter_time_starterr)

    print('CHI SQUARED = {}'.format(summ))

    fig = plt.figure()
    ax = fig.subplots(1,2)
    #ax[0].hist(time_thru_cntr,bins=100,color='r',alpha=0.6,label='Counterclockwise')
    ax[0].hist(counter_shutter_time,bins=10,color='r',alpha=0.6,label='Counterclockwise {:.2f}+/-{:.2f} ms'.format(multi_avg(counter_shutter_time,counter_shutter_timeerr),multi_var(counter_shutter_timeerr)))
    ax[0].hist(clkw_shutter_time,bins=10,color='b',alpha=0.6,label='Clockwise {:.2f}+/-{:.2f} ms'.format(multi_avg(clkw_shutter_time,clkw_shutter_timeerr),multi_var(clkw_shutter_timeerr)))
    #ax[0].hist(time_thru_clkw,bins=100,color='b',alpha=0.6,label='Clockwise')
    ax[0].set_xlabel('Time [ms]')
    ax[0].set_title('Time Through Shutter')
    ax[0].legend()

    ax[1].hist(elapsed_counter,bins=10,color='r',alpha=0.6,label='Counterclockwise')
    ax[1].hist(elapsed_clockw,bins=10,color='b',alpha=0.6,label='Clockwise')
    ax[1].set_xlabel('Time [s]')
    ax[1].set_title('Time From Start')
    ax[1].legend()

    plt.show()


if __name__=="__main__":
    main(sys.argv)
