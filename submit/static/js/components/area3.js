function initArea3(){
    $.ajax({
        url: '/area3/',
        type: 'get',
        async: "false",
        success: function (data) {
            $('#area3').empty().append(data);
            initPie();
        }
    })
}

function initPie() {
    let e = document.getElementById("area3");
    $('#pie_func_type').parent().parent().css("height", e.offsetHeight - 120);
    // 基于准备好的dom，初始化echarts实例
    let myChart = echarts.init(document.getElementById("pie_func_type"));
    let option = {
        title: {
            subtext: 'Proportion of Different Bugs',
            left: 'left'
        },
        tooltip: {
            trigger: 'item'
        },
        // 去掉饼图下方的图例
        // legend: {
        //     bottom: 0
        // },
        series: [
            {
                name: 'type',
                type: 'pie',
                radius: '50%',
                data: [],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };

    function loadData(func_type) {
        let type_num = option.series[0].data.length;
        let is_matched = false;
        for (let i = 0; i < type_num; ++i) {
            if (option.series[0].data[i].name === func_type) {
                option.series[0].data[i].value++;
                is_matched = true;
                break;
            }
        }
        if (!is_matched)
            option.series[0].data.push({value: 1, name: func_type});

        myChart.setOption(option);
    }
    load_pie_data = loadData;
}
