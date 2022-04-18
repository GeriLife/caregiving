document.addEventListener("DOMContentLoaded", function () {
  // Get work summed by type analytics data
  const workByRoleAndTypeSumText = document.getElementById(
    "work-by-role-and-type-sum-data"
  ).textContent;

  console.log(workByRoleAndTypeSumText)
  const workByRoleAndTypeSumData = JSON.parse(workByRoleAndTypeSumText);
  console.log(workByRoleAndTypeSumData);
  
  //workByRoleAndTypeSumData.forEach(item => console.log(item))

  var layout = {
    barmode: "group",
  };

  Plotly.newPlot(
    "work-by-role-and-type-sum-chart",
    workByRoleAndTypeSumData,
    layout
  );
});
