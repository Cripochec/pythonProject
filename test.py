import cv2
import pytesseract
from DBhandler import comparison, open_barrier, standard_view


# Путь к исполняемому файлу Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Символы для сканирования
config = r'-c tessedit_char_whitelist="ABEKMHOPCTYX0123456789"'

# Обученая модель распознавания номерных знаков
plate = cv2.CascadeClassifier('plate.xml')

# Импорт изображения
img = cv2.imread('image.jpg')
# img = cv2.imread('image2.jpg')


# Область сканирования
def scan_area(image, h, w):
    # Получения размера изначального изображения
    height, width, _ = image.shape

    # Размеры правого нижнего угла
    corner_height = int(height * h)  # % от высоты
    corner_width = int(width * w)  # % от ширины

    # Получите правый нижний угол
    corner = image[height - corner_height:height, width - corner_width:width]

    return corner


# Функция подготовки фото к обработкам (обесцвечивание, блюр)
def photo_preparation(image, blur_power, blur_multiplier):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (blur_power, blur_power), blur_multiplier)
    return gray


# Функция определяющая положение номера на изображении
def plate_position(gray, scale_factor, min_neighbors):
    res = plate.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors)
    return res


# Функция отрисовки контуров номера
def plate_contours(res, region, b, g, r, thickness):
    for (x, y, w, h) in res:
        cv2.rectangle(region, (x, y), (x + w, y + h), (b, g, r), thickness=thickness)


# Функция считывание текста c номера
def text_reading(image, res, scale_percent, custom_config):
    for (x, y, w, h) in res:
        plate_image = image[y + 15:y + h - 15, x + 15:x + w - 10]  # 1
        # plate_image = gray[y+10:y + h-7, x-16:x + w+10] # 2

        width = int(plate_image.shape[1] * scale_percent / 100)
        height = int(plate_image.shape[0] * scale_percent / 100)

        dim = (width, height)

        plate_image = cv2.resize(plate_image, dim, interpolation=cv2.INTER_AREA)
        plate_image = cv2.GaussianBlur(plate_image, (3, 3), 1)

        text = pytesseract.image_to_string(plate_image, config=custom_config)
        text = standard_view(text)

        return text


# Функция отрисовки текста c номера на фото
def text_rendering(region, text, res):
    for (x, y, w, h) in res:
        cv2.putText(region, text, (y + h, x + w), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, cv2.LINE_AA)


# Функция проверки номера на совпадение с номерами в БД
def examination(text):
    if comparison(text, ''):
        open_barrier()


# Функция вывода фота на экран
def display_start(region):
    cv2.imshow('camera1', region)
    cv2.waitKey(0)


def main():
    # Обрезанная область изображения
    region = scan_area(img, 0.95, 0.95)

    # Подготовка фото к обработкам (обесцвечивание, блюр)
    gray = photo_preparation(region, 1, 0)

    # Положение номера на изображении
    res = plate_position(gray, 2, 5)

    # Отрисовка контуров номера
    plate_contours(res, region, 0, 0, 255, 3)

    # Считывание текста с номера
    text = text_reading(gray, res, 250, config)

    # Отрисовки текста c номера на фото
    text_rendering(region, text, res)

    # Создание и запуск потоков
    examination(text)
    display_start(region)


if __name__ == '__main__':
    main()
