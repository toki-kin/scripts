#!/bin/dash
set -e
# 使用方法：bash extract_output.sh 输入文件
# 设置Trap
clean_files() {
    if [ -d "${TMPDIR}" ]; then
        echo "Cleaning temp files..."
        rm -rf "${TMPDIR}"
    fi
}
trap "{ clean_files; exit 0; }" EXIT INT

# 检测用法
if [ -z "$1" ]; then
    echo "Usage: bash extract_output.sh INPUT_FILE"
    exit 1
fi

# 检测文件与获取输入文件
if [ -f "$1" ]; then
    sed 's/^[[:space:]]*//g' "$1" | tr -s ' ' >| "${1}.tmp"
    FILE="${1}.tmp"
else
    echo "Usage: $0 filename"
    exit 1
fi

# 检测bc计算器
if ! (command -v bc > /dev/null 2>&1); then
    echo "Please intall bc!"
    exit 1
fi

# 创建临时目录
TMPDIR="$(mktemp -d)"

# 清空输出文件，已排序的和未排序的都是
printf "" >| "output.txt"
printf "" >| "output_unsorted.txt"

split_files() {
    local last_line
    local next_line
    # 上一个划分文件的末行，也是下一个划分文件的首行，很好理解对吧？
    last_line=1
    # 遍历文件，没什么好说的
    for current_line_num in $(seq 1 "$(wc -l < "${FILE}")"); do
        # 这里是获取当前读取到的行的下一行的行号，下面会用到的
        next_line=$((current_line_num + 1))
        # 很吓人对吧？其实只是两个条件并列，第一个条件是当前行的离子结合数量不为0，第二个条件是下一行的离子结合数量为0
        if [ "$(head -n "${current_line_num}" "${FILE}" | tail -n 1 | tr -s ' ' | cut -d ' ' -f 2)" -ne 0 ] && [ "$(head -n "${next_line}" "${FILE}" | tail -n 1 | tr -s ' ' | cut -d ' ' -f 2)" -eq 0 ]; then
            # 获取划分文件，保存在临时目录中
            sed -n "${last_line},${current_line_num}p" "${FILE}" >| "${TMPDIR}/${current_line_num}.tmp.txt"
            last_line=${next_line}
        fi
done
}

# 检查是三列文件还是超三列文件
detect_file() {
    # 很简单的判断方法——第三列往后还有没有内容？
    if [ -z "$(tr -s ' ' < "$1" | cut -d ' ' -f 4-)" ]; then
        return 0
    else
        return 1
    fi
}

# 处理三列文件
process_three() {
    local last_time
    local first_time
    local past
    # 末尾时间毫无疑问就是最后一刻
    last_time=$(tail -n 1 "$1" | tr -s ' ' | cut -d ' ' -f 1)
    # 起始时间就是最后一个结合数为0的行的时间点，你能看明白这里的处理方法吗？
    first_time=$(grep -w '0' "$1" | tail -n 1 | tr -s ' ' | cut -d ' ' -f 1)
    # 使用可恶的bc计算器求间隔时间，保留整数
    past=$(echo "(${last_time}-${first_time})/1" | bc)
    real_first_time=$(echo "${first_time} + 100" | bc)
    # 导出到未排序输出文件中
    echo "${real_first_time} $(tail -n 1 "$1" | tr -s ' ' | cut -d ' ' -f 3) ${past}ps" >> "output_unsorted.txt"
}

# 处理超三列文件
process_morethan() {
    local length
    local longest_line
    local last_time
    local first_time
    local past
    length=0
    # 请原谅我不是很会用awk，只能用这种方法获取最长行
    # shellcheck disable=SC2162
    while read line; do
        if [ "$(echo "${line}" | wc -w)" -gt "${length}" ]; then
            longest_line="${line}"
            length=$(echo "${line}" | wc -w)
        fi
    done < "$1"
    # 伪数组，其实就是空格分隔的列表
    the_array="$(echo "${longest_line}" | tr -s ' ' | cut -d ' ' -f 3-)"
    # 遍历数组，获取每个离子的结合时间
    for i in ${the_array}; do
        # 用grep获取所有包含指定离子的行，并且获取最后一刻
        last_time=$(grep "${i}" "$1" | tail -n 1 | tr -s ' ' | cut -d ' ' -f 1)
        # 反过来说就是第一时刻
        first_time=$(grep "${i}" "$1" | head -n 1 | tr -s ' ' | cut -d ' ' -f 1)
        # 同上
        past=$(echo "(${last_time}-${first_time})/1 + 100" | bc)
        echo "${first_time} ${i} ${past}ps" >> "output_unsorted.txt"
    done
}

# 进入程序
split_files "${FILE}"
# shellcheck disable=SC2045
for i in "${TMPDIR}"/*; do
    if (detect_file "${i}"); then
        process_three "${i}"
    else
        process_morethan "${i}"
    fi
done
# 文件排序，对于是否需要去重表示怀疑，因此不加入选项
sort -k 1 -n -o "output.txt" < "output_unsorted.txt"
