<?php
  function deviceHeader($deviceID) {
    echo "<section id=\"".$deviceID."\">\n";
    #<a id="backtopoll"></a>
    echo "<h2>$deviceID</h2>\n";
  }

#  function build_radio_input($formName,) {
#    return("onchange=\"('#$formName')submit();\""
#  }

  function get_status() {
    $inData = file_get_contents("http://127.0.0.1:5000/api/status" );
    $devicesOBJs = json_decode($inData);
    return $devicesOBJs;
  }

  function outputDeviceInfo($devicesOBJs) {
    foreach($devicesOBJs->devices as $curDev) 
      if ($curDev->devType == 'Relay')
        output_relay_type($curDev);

    echo "<br>\n";

    foreach($devicesOBJs->devices as $curDev)
      if ($curDev->devType == 'Sensor')
        output_sensor_type($curDev);
  }

  function output_page_header() {
    echo "<!DOCTYPE HTML>";

    echo "<html><head><title>";

    echo "status";
  
    echo "</title>";
    echo "<script src=\"jquery-2.1.1.js\"></script>";
    echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n";
    echo "<META HTTP-EQUIV=\"refresh\" CONTENT=\"15\">\n";
    echo "</head>";
  }

  function output_page_trailer() {
    echo "</html>";
  }

  function output_relay_type($curDev) {

    deviceHeader($curDev->deviceID);


    echo "<div class=\"state\">\n";
    echo "<form id=\"State-$curDev->deviceID\" action=\"interface.php#$curDev->deviceID\" method=\"POST\">\n";  
      echo "<h3>Current State</h3>\n";
      if ($curDev->override == "auto")
        echo $curDev->curState;
      else {
        echo "Off";
        echo "<input type=\"radio\" name=\"manual[$curDev->deviceID]\" onchange=\"$('#State-$curDev->deviceID').submit();\" value=\"Off\"" ;
        if ($curDev->curState == "Off") echo " checked ";
        echo ">\n"; 
        echo "On";
        echo "<input type=\"radio\" name=\"manual[$curDev->deviceID]\" onchange=\"$('#State-$curDev->deviceID').submit();\" value=\"On\"" ;
        if ($curDev->curState == "On") echo " checked ";
        echo ">\n"; 
      }
    echo "</form>\n";
    echo "</div>";


    echo "<form id=\"Override-$curDev->deviceID\" action=\"interface.php#$curDev->deviceID\" method=\"POST\">\n";  
    echo "<div class=\"override\">\n";
      echo "<h3>Override</h3>\n";
      echo "Off";
      echo "<input type=\"radio\" name=\"override[$curDev->deviceID]\" onchange=\"$('#Override-$curDev->deviceID').submit();\" value=\"auto\"" ;
#      echo "<input type=\"radio\" name=\"override[$curDev->deviceID]\"".build_onchange("Override-$curDev->deviceID")." value=\"auto\"" ;
      if ($curDev->override == "auto") echo " checked ";
      echo ">\n"; 
      echo "On";
      echo "<input type=\"radio\" name=\"override[$curDev->deviceID]\" onchange=\"$('#Override-$curDev->deviceID').submit();\" value=\"manual\"" ;
      if ($curDev->override == "manual") echo " checked ";
      echo ">\n"; 

    echo "</form>\n";
    echo "</div>";


    
    echo "</section>\n";
  }

  function output_sensor_type($curDev) {
    deviceHeader($curDev->deviceID);
    echo "<div class=\"sensor\">\n";
      
      echo "<h3>Real Value</h3>\n";
      printf("%.2f</br></br>\n",$curDev->value);
      echo "Raw Value: ";
      printf("%.2f\n",$curDev->rawValue);

    echo "</div>";
    echo "</section>\n";
  }

  ###########################################################
  # main processing

  foreach($_POST as $key => $inArray) {
    if ($key == "override") {
      foreach($inArray as $deviceID => $value) {
        $postdata = http_build_query(
          array(
            'deviceID' => $deviceID,
            'action'   => $value )
        );
        $opts = array('http' =>
            array(
                'method'  => 'POST',
                'header'  => 'Content-type: application/x-www-form-urlencoded',
                'content' => $postdata
            )
        );
        $context  = stream_context_create($opts);
        $result = file_get_contents('http://127.0.0.1:5000/api/override', false, $context);

        print_r($result); 
      }
    }
    else if ($key == "manual") {
      foreach($inArray as $deviceID => $value) {
        $postdata = http_build_query(
          array(
            'deviceID' => $deviceID,
            'action'   => $value )
        );
        $opts = array('http' =>
            array(
                'method'  => 'POST',
                'header'  => 'Content-type: application/x-www-form-urlencoded',
                'content' => $postdata
            )
        );
        $context  = stream_context_create($opts);
        $result = file_get_contents('http://127.0.0.1:5000/api/manual', false, $context);
      }

    }
  }


  output_page_header();

  $devicesOBJs = get_status();
 
  print_r($_POST);
  echo "<hr>\n";

    
  outputDeviceInfo($devicesOBJs);
  echo "<br><hr>\n";

  print_r($devicesOBJs);
/*
  }$key => $curVal) {
    if ( is_array($curVal) ) {
      echo "$key:<br>\n"; 
      array_iterate($curVal,0);
    }
    else 
      echo "$key = $curVal<br>\n";
  }

*/

  output_page_trailer();
?>
