function deleteJob(jobId) {
    fetch("/delete-job", {
      method: "POST",
      body: JSON.stringify({ job_Id: jobId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

function applyForThisJob(jobId){
    fetch("/uploadCV", {
        method: "POST",
        body: JSON.stringify({ job_Id: jobId }),
      }).then((_res) => {
        window.location.href = "/uploadCV";
      });
}
function isNumberKey(evt) {
    var charCode = (evt.which) ? evt.which : evt.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    return true;
}
