import math
import chempy
from chempy import balance_stoichiometry
from pprint import pprint
from chempy import Substance
from docxtpl import DocxTemplate

"""Расчет требуемого количества кислорода для окисления органических соединений сырья"""

"""Исходные данные по туннелю и технологическим параметрам"""
l = 22      # длина туннеля, м
b = 7       # ширина туннеля, м
s = 7 * 22  # плошадь загрузки тоннеля
h = 2.6  # высота загрузки сырья, м
day_composting = 21  # количество дней компостирования, дни
t_day = 24  # количество часов работы в сутки, ч

"""Исходные данные по сырью"""
p = 0.65  # плотность сырья, т/м3
w = 60  # влажность сырья, %
air_density = 1.2  # плотность воздуха при н.у., 1.2 кг/м3
del_org = 60  # доля органики в объема отхода, %
del_org_part = 1  # доля вида органического отхода в общей массе органических отходов
degradability = 0.7  # доля биоразлагаемого материала
mol_formula = 'C16H27O8N'  # химическая формула органического компонента сырья (менять вручную)

"""Расчет стехиометрических коэффициентов уравнения"""

reac, prod = balance_stoichiometry({mol_formula, 'O2'}, {'CO2', 'H2O', 'NH3'})  # получение коэф. хим. реакции
pprint(f'Коэффициенты перед исходными веществами {dict(reac)}')
pprint(f'Коэффициенты перед продуктами реакции {dict(prod)}')
print(reac[mol_formula])


def molecule_mass():
    """
    Расчет молекулярной массы окисляемого сырья
    :return: float, молекулярная масса окисляемого вещества
    """
    material = Substance.from_formula(mol_formula)
    mass = material.mass
    return mass


print(f'Молекулярная масса органического вещества M = {molecule_mass()}, г/моль')


def amount_oxygen():
    """
    Расчет количества кислорода, необходимого для окисления органики данного компонента сырья
    :return: количество кислорода, г О2 /г биоразлогаемых элементов (без учета доли биоразлагаемого материала в органике)
    """
    molecular_mass = Substance.from_formula(mol_formula)  # передача формулы для получения молекулярной массы
    mol_mass_float = molecular_mass.mass  # молекулярная масса, г/моль
    x = 32 * float(reac['O2']) / mol_mass_float  # количество кислорода
    return round(x, 2)


print(f'Количество кислорода для окисления 1 г органического компонента - {amount_oxygen()}')


def amount_oxygen_ammonia():
    """
    Расчет количества кислорода для окисления аммиака
    :return: float, количество кислорода для окисления аммиака, г О2/ 1 г NH3
    """
    molecular_mass = Substance.from_formula(mol_formula)
    x = 2 * 32 / molecular_mass.mass  # расчет количества кислорода на окисление аммиака
    return round(x, 3)


print(f'Количество кислорода на окисление аммиака - {amount_oxygen_ammonia()}, г')


def amount_oxygen_glucose():
    """
    Расчет количества кислорода для окисления углеводорода
    :return: float, количество кислорода для окисления углеводорода, г О2/ 1 г
    """
    x = 6 * 32 / 162  # расчет количества кислорода на окисление углеводорода (в знаменателе мол. массы углеводорода, в
    # в числителе количество молекул кислорода, умноженное на мол. массу кислорода
    return round(x, 3)


print(f'Количество кислорода на окисление целлюлозы - {amount_oxygen_glucose()}, г')


def quantity_air():
    """
    Расчет количества воздуха для обеспечения требуемого количества органики
    :return: float, количество воздуха на 1 гр органики для окисления
    """
    concentration_oxygen = 0.21  # концентрация кислорода в воздухе, 21%
    q = amount_oxygen() / concentration_oxygen  # количество воздуха для обеспечения требуемого количества О2
    return round(q, 1)


print(f'Количество воздуха для обеспечения требуемого количества О2 на 1гр органики - {quantity_air()}')


def mass_org_waste():
    """
    Расчет массы органической части сырья
    :return: float, масса компонента органики, т
    """
    general_volume = s * h  # объем загрузки всего сырья в туннеле, м3
    general_mass = general_volume * p  # расчет массы всего сырья, т
    dry_mass_waste = general_mass * (1 - (w / 100))  # масса сухого сырья
    mass_org_part = dry_mass_waste * (del_org / 100) * del_org_part  # масса конкретного вида органического отхода
    return round(mass_org_part, 2)


print(f'Масса конкретного органического компонента, {mass_org_waste()}, т')


def bvs():
    """
    Расчет массы биоразлагаемого материала, т BVS
    :return: float, масса биоразлагаемой массы сырья
    """
    m = mass_org_waste() * degradability
    return round(m, 3)


print(bvs())


def amount_oxygen_bvs():
    """
    Определение количества кислорода для окисления BVS (сухое, биоразлагаемое сырье)
    :return: float, количество воздуха для разложения BVS, т
    """
    x = round(bvs() * amount_oxygen(), 2)
    return x


print(f'Количество О2 для разложения BVS = {amount_oxygen_bvs()}, т')


def air_request():
    """
    Расчет количества воздуха для окисления BVS
    :return: float, масса воздуха для окисления BVS, т
    """
    q = amount_oxygen_bvs() / 0.21
    return round(q, 1)


print(f'Количества воздуха для окисления BVS = {air_request()}, т')


def consumption_air():
    """
    Расчет объема воздуха для окисления BVS
    :return: float, объем воздуха за цикл компостирования, м3
    """
    q = (air_request() * 1000) / air_density
    return round(q, 1)


print(f'Объем воздуха для окисления BVS = {consumption_air()}, м3')


def hour_consumption_air():
    """
    Расчет равнораспределенного часового расхода для обеспечения требуемого количества О2
    :return: float, средний часовой расход воздуха (без учета пиковых значений)
    """
    q_h = math.ceil(consumption_air() / (day_composting * t_day))
    return q_h


print(f'Усредненный часовой расход = {hour_consumption_air()}, м3/ч')


def oxygen_bvs():
    """
    Расчет количества кислорода, необходимого для окисления 1г сухого BVS
    :return: float, г О2 / г сух. вещества
    """
    q_ox = round(degradability * amount_oxygen(), 2)
    return q_ox


print(
    f'Количество кислорода на окисление BVS с учетом биоразлагаемого материала = {oxygen_bvs()}, г О2/ г сух BVS')


def oxygen_glucose():
    """
    Расчет количества кислорода при окислении 1г целлюлозы
    :return: float, количества кислорода с учетом степени разложения органики = 0,25
    """
    q_ox_glu = round(0.25 * amount_oxygen_glucose(), 2)
    return q_ox_glu


print(f'Количество кислорода на окисление целлюлозы с учетом степени разложения 0,25 = {oxygen_glucose()}, г О2')


def cal_amount():
    """
    Расчет количества калорий при окислении 1 гр BVS и целлюлозы
    :return: float, количество калорий на окисление 1 гр BVS и органики
    """
    x = (oxygen_bvs() + oxygen_glucose()) * 3260  # выделение тепла на 1 гр органики BVS и целлюлозы, 3260 - количество

    # кал, переносимые 1 молекулой О2
    return round(x, 1)


print(f'Количество выделяющегося тепла при окислении 1 гр органики (BVS, целлюлоза) - {cal_amount()}, кал/1 гр сух. '
      f'органики')


def consumption_air_heat():
    """
    Расчет количества воздуха для удаления теплоизбытков
    :return: float, г воздуха / 1 г сухого BVS
    """
    q = round(cal_amount() / (60.57 + 1.77 + 8.40), 2)
    return q


print(f'Количество воздуха для удаления теплоизбытков при окислении 1 гр BVS = {consumption_air_heat()}, г возд./1 г BVS')


def sum_hour_air_consumption():
    """
    Расчет усредненного часового расхода воздуха для удаления теплоизбытков
    :return: float, м3/ч
    """
    q_air = (consumption_air_heat() * 10**6) / (1.2 * day_composting * t_day * 1000)
    q_summ = math.ceil(q_air * mass_org_waste())
    return [q_summ, q_air]


print(f'Усредненный часовой расход для удаления теплоизбытков составит Q = {sum_hour_air_consumption()}, м3/ч')


"""Подготовка отчета по расчету"""

# doc = DocxTemplate('Template air consumption.docx')
# context = {'mol_formula': mol_formula, 'l': l, 'b': b, 'h': h, 'p': p, 'air_density': air_density, 'del_org': del_org,
#            'degradability': degradability, 'w': w, 'day_composting': day_composting, 't_day': t_day,
#            'koeff1': reac[mol_formula], 'koeff2': reac['O2'], 'koeff3': prod['CO2'], 'koeff4': prod['H2O'],
#            'koeff5': prod['NH3'], 'molecule_mass': molecule_mass, }
# doc.render(context)
# doc.save('Calculation.docx')


def peak_oxygen():
    """
    Расчет пикового значения кислорода для удаления избытков тепла
    :return: float, количество кислорода в час при пиковых потреблениях
    """
    # q_peak = 14 / 1000      # пиковое значение кислорода при 65 С, г
    q_air_peak = sum_hour_air_consumption()[0] * 0.3 + sum_hour_air_consumption()[0]
    return q_air_peak


print(f'Количество воздуха в пиковые моменты потребления {peak_oxygen()}, м3/ч')


print(peak_oxygen.__doc__)
