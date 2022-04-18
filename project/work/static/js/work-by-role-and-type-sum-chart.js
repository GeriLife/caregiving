document.addEventListener("DOMContentLoaded", function () {
    var workByRoleAndTypeSumChartElement = document.getElementById(
      "work-by-role-and-type-sum-chart"
    );
    var workByRoleAndTypeSumChart = echarts.init(
      workByRoleAndTypeSumChartElement
    );
    var workByRoleAndTypeSumChartOptions;
  
    // Get work summed by type analytics data
    const workByRoleAndTypeSumText = document.getElementById(
      "work-by-role-and-type-sum-data"
    ).textContent;
    const workByRoleAndTypeSumData = JSON.parse(workByRoleAndTypeSumText);
  
    workByRoleAndTypeSumChartOptions = {
      dataset: {
        dimensions: [
            { name: "role_name", type: "categorical", },
            { name: "work_type", type: "categorical", },
            { name: "total_minutes", type: "int", },
        ],
        source: workByRoleAndTypeSumData,
      },
      title: {
        top: 30,
        left: "center",
        text: "Caregiving minutes by role and work type",
      },
      xAxis: {
        name: "Caregiver role and work type",
        nameLocation: "middle",
        nameGap: 30,
        type: "category",
      },
      yAxis: {
        name: "Minutes",
        nameLocation: "middle",
        nameGap: 30,
        nameRotate: 90,
        type: "value",
      },
      series: [
        {
          type: "bar",
        },
        {
          type: "bar",
        },
      ],
    };
  
    workByRoleAndTypeSumChart.setOption(workByRoleAndTypeSumChartOptions);
  });
  