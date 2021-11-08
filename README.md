[![E+E_Logo](./images/epluse-logo.png)](https://www.epluse.com/en/)

# EE895 I2C with Raspberry Pi


![EE895](./images/EE895-co2-element.png)  


[![button1](./images/learn-more.png)](https://www.epluse.com/en/products/co2-measurement/co2-sensor/ee895/)   [![button2](./images/data-sheet.png)](https://downloads.epluse.com/fileadmin/data/product/ee895/datasheet_EE895.pdf) 



## QUICK START GUIDE  

### Components 
- EE895
- Raspberry Pi 4
- Breadboard 
- Wire jumper cable <br>

| Step |                                                                                                                                                             |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | Connect the EE895 sensor module with Raspberry Pi according to the following scheme: <br> [<img src="images/EE895_rpi.PNG" width="50%"/>](images/EE895_rpi.PNG)|
| 2    | Download and install the operating system (https://www.raspberrypi.org/software/operating-systems/).                                                            |
| 3    | Boot Raspberry Pi and complete any first-time setup if necessary (find instructions online).                                                                |
| 4    | Activate I2C communication:https://github.com/fivdi/i2c-bus/blob/master/doc/raspberry-pi-i2c.md                     |
| 5    | Download and install the "smbus2" library on the Raspberry Pi. [Instruction](https://pypi.org/project/smbus2/#:~:text=Installation%20instructions)            |
| 6    | Clone the repository: ```git clone https://github.com/EplusE/ee895_i2c_rpi.git```             |
| 7    | Open a command shell and type following command to receive measurement data – that’s it!  |

### Example output

```shell
pi@raspberrypi:~ $ python3 ee895_i2c_rpi.py
	temperature, CO2, pressure
	23.41 °C, 500 ppm, 978.1 mbar 
```
<br>



<br>

## License 
See [LICENSE](LICENSE).
