import country_converter as coco
import countrynames


def main():
    print(coco.convert(names=countrynames.to_code('Greenland'), to='EU'))


main()
