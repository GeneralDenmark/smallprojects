#!/usr/bin/env bash
declare -a to_be_printed
declare display_all
function usage
{
    echo "AGW selvudviklingsdags deal script :p"
    echo "usage: funny_deal.bash ((-a|-h)|[1-9]+)"
    echo "   ";
    echo "  -a | --all               : Print everything";
    echo "  -h | --help              : This message and exit";
    echo "  1-9                      : displays the relevant paragraph"
    echo "    ";
    echo "AGW"
}
function parse_args
{
  while [ "$1" != "" ]; do
      case "$1" in
          -a | --all  )              display_all=1               ;;
          -h | --help )              usage;                  exit;;
          *           )              show_paragraphs $(echo $1 | grep -o .) ;;
      esac
      shift
  done

}

function show_paragraphs {
    for i in "$@"; do
        if [[ $i =~ ^-?[0-9]$ ]] ; then
            to_be_printed+=($i)
        else
            echo "Error argument not understood: $i"
            usage
            exit
        fi
    done
}

function prefix {
    if $1 ; then
        echo "§$2. $3"
    else
        echo "    $2. $3"
    fi
}


function init {
    num_days=$3
    start_date=$4
    prefix true "0" "$2 vil optjene $3 dag for hver afsluttede måned startende: $4"
    prefix false "a" "Disse dage vil blive kaldt for selvudviklingsdage. "
    return 1
}

function _1 {
    prefix true "1" "Selvudviklingsdage er selv administreret. "
    prefix false "a" "Dette betyder at hvilken teknologi der bliver fokuseret på, afhænger af $2."
    prefix false "b" "Omend selvudviklingsdagen kan blive brugt på et vilkårligt tidspunkt, skal dette følge foregående aftale med nærmeste leder. "
}
function _2 {
    prefix true "2" "Hver dag optjent skal bruges inden for $4 måneder af dets oprindelse. F.eks.: "
    echo "         dage optjent $6 skal bruges inden $(date -d "$6+$4 months" '+%Y/%m/%d')"
}
function _3 {
    prefix true "3" "Selvudviklingsdagene kan bruges I forlængelse af hinanden. "
}
function _4 {
    prefix true "4" "Der er ingen krav til hvor selvudviklingsdage bliver holdt, så længe præmissen for dagen stadig kan blive overholdt. "
}
function _5 {
    prefix true "5" "Efter en selvudviklingsdag, skal $2 skrive $5 side teknologien, hvor denne kan bruges I relation til BVVS, hvis denne kan bruges, samt efter krav kunne lave en kort mundlig præsentation af teknologiens fordele samt ulemper. "
}

function main(){
    current_count=0
    _receiver="Asger"
    _days=1
    _expire_month=12
    _pages_to_write="1/2"
    _start_date="2019/05/01"
    parse_args "$@"
    echo "So I made this script so that a super serious thing like this would be a bit less boring :)"
    init $current_count $_receiver $_days $_start_date
    ((current_count++))
    if [[ $display_all -eq 1 ]]; then
        to_be_printed+=(1 2 3 4 5)
    fi
    for i in "${to_be_printed[@]}"; do
        _$i $current_count $_receiver $_days $_expire_month $_pages_to_write $_start_date
        ((current_count++))
    done
}

main "$@"