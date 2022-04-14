document.addEventListener("DOMContentLoaded", function () {
  var workByTypeSumChartElement = document.getElementById(
    "work-by-type-sum-chart"
  );
  var workByTypeSumChart = echarts.init(workByTypeSumChartElement);
  var workByTypeSumChartOptions;

  // Get work summed by type analytics data
  const workByTypeSumText = document.getElementById(
    "work-by-type-sum-data"
  ).textContent;
  const workByTypeSumData = JSON.parse(workByTypeSumText);

  workByTypeSumChartOptions = {
    dataset: {
      dimensions: ["type__name", "total_minutes"],
      source: workByTypeSumData,
    },
    title: {
      top: 30,
      left: "center",
      text: "Caregiving minutes by type of work",
    },
    xAxis: {
      name: "Type of work",
      nameLocation: "middle",
      nameGap: 30,
      type: "category",
    },
    yAxis: {
      name: "Minutes",
      nameLocation: "middle",
      nameGap: 30,
      type: "value",
    },
    series: [
      {
        type: "bar",
      },
    ],
  };

  workByTypeSumChart.setOption(workByTypeSumChartOptions);
});
