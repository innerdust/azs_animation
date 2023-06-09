import traffic_analysis


#===ФОрмирование карты дорожного покрытия (15х15)
def model_settings(grids=15,lanes=13,length=200):
    os.system("netgenerate --grid --grid.number=5 -L="+str(lanes)+" --grid.length="+str(length)+" --output-file=grid.net.xml")

# ===Функция запуска одной симуляции
def Func_OneStep(loc_p,loc_ev):
    #генерация случайных маршрутов заданного количества электромобилей
    temp_str =  "randomTrips.py -n grid.net.xml -o flows.xml --begin 0 --end 1 --period 1 --flows " + str(loc_ev)
    os.system(temp_str)
    #генерация маршрутов отдельных электромобилей с добавлением характеристик батареи
    os.system("jtrrouter --flow-files=flows.xml --net-file=grid.net.xml --output-file=grid.rou.xml --begin 0 --end 10000 --accept-all-destinations")
    os.system(loc_p + "generateContinuousRerouters.py -n grid.net.xml --end 10000 -o rerouter.add.xml")
    #подготовка симуляции
    model_tree = ET.parse("grid.sumocfg")
    model_root = model_tree.getroot()
    for curr_child in model_root:
        if (curr_child.tag == 'output'):
            for curr_child_2 in curr_child:
                curr_child_2.attrib['value'] = 'grid.output'+str(loc_ev)+'.xml'
    with open('grid.sumocfg', 'wb') as f:
        model_tree.write(f)
    #запуск симуляции
    os.system("sumo -c grid.sumocfg --device.fcd.period 100")

#===Функция конвертации результатов симуляции в текстовую форму
def Func_ResConvertToText(loc_ev):
    model_tree = ET.parse("grid.output"+str(loc_ev)+".xml")
    model_root = model_tree.getroot()

    length_curr = 0
    for model_child in model_root:
        for model_child_2 in model_child:
            length_curr += 1

    velocitys_ind = 0
    times_ind = 0
    attrib_curr = ''
    # выходные параметры моделирования
    velocitys_result = np.zeros(length_curr)
    times_result = np.zeros(length_curr)
    ids_result = np.zeros(length_curr)
    for model_child in model_root:
        for model_child_2 in model_child:
            if (model_child_2.tag == 'vehicle'):
                attrib_curr = (model_child_2.attrib)
                velocitys_result[velocitys_ind] = float(attrib_curr['speed'])
                ids_result[velocitys_ind] = float(attrib_curr['id'])
                times_result[velocitys_ind] = times_ind
                velocitys_ind = velocitys_ind + 1
        times_ind = times_ind + 1
    Res = np.c_[ids_result, times_result, velocitys_result]

    ResQuantity = len(np.unique(Res[:, 1]))
    vel_param = np.zeros(ResQuantity)
    nc_param = np.zeros(ResQuantity)
    flux_param = np.zeros(ResQuantity)

    for i in range(0, ResQuantity):
        x_ind = np.where(Res[:, 1] == i)
        vel_param[i] = np.mean(Res[x_ind, 2])
        nc_param[i] = len(x_ind[0])
        flux_param[i] = np.sum(Res[x_ind, 2])
        vel_arr = np.c_[nc_param, vel_param, flux_param]

    np.savetxt('v'+str(loc_ev)+'.txt',vel_arr)

#=====Основная программа
if __name__ == '__main__':
    import os
    import numpy as np

    import xml.etree.ElementTree as ET
    my_path = "C:\\Program Files (x86)\\Eclipse\\Sumo\\Tools\\"       #путь к утилитам sumo
    model_settings()        # инициализация карты
    EV_Array=np.r_[np.linspace(10,100,10).astype(int),np.linspace(100,2000,20).astype(int)]
    for i in range(0,len(EV_Array)):
        Func_OneStep(my_path,EV_Array[i])
        Func_ResConvertToText(EV_Array[i])
    print(np.r_[np.linspace(10,100,10).astype(int),np.linspace(100,2000,20).astype(int)])
    traffic_analysis.plots(EV_Array)





