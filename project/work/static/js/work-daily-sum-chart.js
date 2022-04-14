document.addEventListener("DOMContentLoaded", function () {
  var workDailySumChartElement = document.getElementById(
    "work-daily-sum-chart"
  );
  var workDailySumChart = echarts.init(workDailySumChartElement);
  var workDailySumChartOptions;

  // TODO: determine how to dynamically select the chart year
  // E.g. with the current year or based on user selection
  const chartYear = "2022";

  // Get daily sum analytics data
  const workDailySumText = document.getElementById(
    "work-daily-sum-data"
  ).textContent;
  const workDailySumData = JSON.parse(workDailySumText);
  const workDailySumMaxText = document.getElementById(
    "work-daily-sum-max-data"
  ).textContent;
  const workDailySumMaxData = JSON.parse(workDailySumMaxText);

  workDailySumChartOptions = {
    title: {
      top: 30,
      left: "center",
      text: "Daily Caregiving Minutes",
    },
    tooltip: {},
    visualMap: {
      min: 0,
      max: workDailySumMaxData,
      type: "piecewise",
      orient: "horizontal",
      left: "center",
      top: 65,
    },
    calendar: {
      dayLabel: {
        firstDay: 1,
        // TODO: enable Finnish locale
        // https://echarts.apache.org/en/option.html#calendar.dayLabel.nameMap
        nameMap: "en",
      },
      monthLabel: {
        // TODO: enable Finnish locale
        // https://echarts.apache.org/en/option.html#calendar.monthLabel.nameMap
        nameMap: "en",
      },
      top: 120,
      left: 30,
      right: 30,
      cellSize: ["auto", 14],
      // TODO: determine how best to choose the data range
      // e.g. data min/max?
      // Note: this may affect the chart layout,
      // which currently has a hard-coded height
      range: chartYear,
      itemStyle: {
        borderWidth: 0.5,
      },
      yearLabel: { show: true },
    },
    dataset: {
      dimensions: ["date", "total_minutes"],
      source: workDailySumData,
    },
    series: {
      type: "heatmap",
      coordinateSystem: "calendar",
    },
  };

  workDailySumChart.setOption(workDailySumChartOptions);
});
