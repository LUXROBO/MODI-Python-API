import modi
import time


if __name__ == "__main__":

    print("Program Start")
    bundle = modi.MODI()
    # button = bundle.buttons[0]
    # gyro = bundle.gyros[0]
    motor = bundle.motors[0]
    # while button.double_clicked() != True:
    for i in range(1, 50, 1):
        k = i * 1.0
        motor.speed(k, -k)
        # print('dX, dY, Dz, aX aY aZ gX gY gZ',
        #         gyro.pitch(),
        #         gyro.roll(),
        #         gyro.yaw(),
        #         gyro.acceleration_x(),
        #         gyro.acceleration_y(),
        #         gyro.acceleration_z(),
        #         gyro.angular_vel_x(),
        #         gyro.angular_vel_y(),
        #         gyro.angular_vel_z(),
        #         # bundle._recv_q.qsize()
        #     )

        print("i am alive")
        # time.sleep(0.1)
    motor.speed(0.0, 0.0)
    time.sleep(0.1)
    bundle.end()
    bundle2.end()
    print("Program End")
