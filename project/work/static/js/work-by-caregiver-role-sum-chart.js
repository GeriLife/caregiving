document.addEventListener("DOMContentLoaded", function () {
  var workByCaregiverRoleSumChartElement = document.getElementById(
    "work-by-caregiver-role-sum-chart"
  );
  var workByCaregiverRoleSumChart = echarts.init(
    workByCaregiverRoleSumChartElement
  );
  var workByCaregiverRoleSumChartOptions;

  // Get work summed by type analytics data
  const workByCaregiverRoleSumText = document.getElementById(
    "work-by-caregiver-role-sum-data"
  ).textContent;
  const workByCaregiverRoleSumData = JSON.parse(workByCaregiverRoleSumText);

  workByCaregiverRoleSumChartOptions = {
    dataset: {
      dimensions: ["caregiver_role__name", "total_minutes"],
      source: workByCaregiverRoleSumData,
    },
    title: {
      top: 30,
      left: "center",
      text: "Caregiving minutes by caregiver role",
    },
    xAxis: {
      name: "Caregiver role",
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
    ],
  };

  workByCaregiverRoleSumChart.setOption(workByCaregiverRoleSumChartOptions);
});
