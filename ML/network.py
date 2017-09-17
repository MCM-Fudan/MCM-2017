import xlrd
import math
import numpy
from sklearn import preprocessing
from sklearn.neural_network import MLPRegressor
from sklearn.cross_validation import train_test_split
from numpy import loadtxt, where
from pylab import scatter, show, legend, xlabel, ylabel


if __name__ == '__main__':
    fitem_name = "old_mission.xls"
    staff_name = "user.xlsx"
    fitem_data = xlrd.open_workbook(fitem_name)

    try:
        fitem_sh = fitem_data.sheet_by_name("t_tasklaunch")
    except:
        print("no sheet in %s named t_tasklaunch" %fitem_name)


    staff_data = xlrd.open_workbook(staff_name)
    try:
        staff_sh = staff_data.sheet_by_name("Sheet1")
    except:
        print("no sheet in %s named Sheet1" %staff_name)

    fitem = []
    staff = []

    for i in range(0, fitem_sh.nrows):
        row_data = fitem_sh.row_values(i)
        fitem.append(row_data)

    for i in range(0, staff_sh.nrows):
        row_data = staff_sh.row_values(i)
        x, y = row_data[1].split()
        row_data[1] = x
        row_data.insert(2, y)
        staff.append(row_data)

    radius = 1000
    feature_mat = []
    price_vec = []
    for l in fitem :
        no_within_r = 0
        avg_dis = 0
        avg_credit = 0
        avg_time = 0
        avg_item = 0
        for s in staff :
            dis = math.sqrt((float(l[1])*11132 - float(s[1])*11132)**2 + (float(l[2])*10000 - float(s[2])*10000)**2)
            if(dis < radius) :
                no_within_r += 1
                avg_dis += dis
                avg_credit += s[5]
                avg_time += s[4]
                avg_item += s[3]
        if(no_within_r != 0) :
            avg_dis /= no_within_r
            avg_credit /= no_within_r
            avg_time /= no_within_r
            avg_item /= no_within_r
            feature_mat.append([no_within_r, avg_dis, avg_credit, avg_time, avg_item])
            price_vec.append(l[3])

    scaler = preprocessing.MinMaxScaler(feature_range=(-1,1))
    mat = numpy.array(feature_mat)
    mat = scaler.fit_transform(mat)
    price_vec = numpy.array(price_vec)

    #ftrain, ftest, ptrain, ptest = train_test_split(mat, price_vec, test_size=0.1)

    clf = MLPRegressor(solver='lbfgs', hidden_layer_sizes=(4, 4, 4), random_state=1)
    clf.fit(ftrain, ptrain)
    result = clf.predict(ftest)
    print(result)
    print(len(result))

    print(ptest)
    print(len(ptest))
    print('score sklearn :', clf.score(ftest,ptest))
    print(clf.get_params())

    # pos = where(sign_vec == 1)
    # neg = where(sign_vec == 0)
    # scatter(mat[pos, 0], mat[pos, 1], marker='o', c='b')
    # scatter(mat[neg, 0], mat[neg, 1], marker='x', c='r')
    # xlabel('Exam 1 score')
    # ylabel('Exam 2 score')
    # legend(['Not Admitted', 'Admitted'])
    # show()


