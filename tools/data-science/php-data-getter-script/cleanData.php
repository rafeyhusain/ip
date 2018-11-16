<?php
/**
 * #Command used to create data :
 *
 * es2csv -s 50000 -i product_sg -D product -f category.url masterbrain -r -q @'query.json' --verify-certs -u https://iprice:fGcXoXcBtYaWfUpE@es-qa.ipricegroup.com:443 -o database.csv
 *
 * #then run :
 * php cleandata.php
 **/
//handle Arguments
/**
 * force : Fresh force
 * min   : min Threshold
 * max   : max Threshold
 **/
$options = getopt('n:x:o:f::h::', array('min:', 'max:', 'force::', 'help::', 'output:', 'second-level::'));
if (isset($options['help'])) {
    echo "--force : Fresh force\r\n";
    echo "--min   : Min Threshold, should provide value \r\n";
    echo "--max   : Max Threshold, should provide value \r\n";
    echo "--second-level   : Max Threshold, should provide value \r\n";
    echo "--output   : Output folder \r\n";
    echo "--help   : Help List \r\n";
    die();
    exit;
}

// deal with options
$minMasterbrainLength = 10;
$threshold_min = isset($options['min']) ? intval($options['min']) : 200;
$threshold_max = isset($options['max']) ? intval($options['max']) : 10000;
$path = isset($options['output']) ? $options['output'] : '.';
$path = $path . '/';
if (!file_exists($path)) {
    mkdir($path, 0777, true);
}
$forceFresh = isset($options['force']) ? true : false;
$secondLevel = isset($options['second-level']) ? true : false;
$trainingPercentage = 0.8;

function openFile($filename, $mode, $alternatePath = null)
{
    $tmpPath = $alternatePath ?? $path;
    return fopen($tmpPath . $filename, $mode);
}

$row = 1;
$statsFile = 'statsFile.json';
$stats = json_decode(file_get_contents($statsFile), true);
echo "\r\nCleaning the Data.. \r\n";
if (empty($stats) || $forceFresh) {
    $stats = [];
    $handleClean = openFile("database_cleaned.csv", "w");
    if (($handle = openFile("database.csv", "r", './')) !== FALSE) {
        $data = fgetcsv($handle);
        while (($data = fgetcsv($handle)) !== FALSE) {
            $num = count($data);
            $row++;
            $rowData = [];
            $skip = false;
            if ($row % 1000 == 0) {
                echo '.';
            }
            for ($c = 0; $c < $num; $c++) {
                if ($c == 0) {
                    if (strlen($data[$c]) < 2) {
                        $skip = true;
                        break;
                    }
                    if ($secondLevel) {
                        preg_match('/([a-z|A-Z|0-9|-]*\/[a-z|A-Z|0-9|-]*).*$/', $data[$c], $matches);
                        $cat = $matches[1];
                    } else {
                        $cat = $data[$c];
                    }
                    if (!isset($stats[$cat])) {
                        $stats[$cat] = [];
                        $stats[$cat]['freq'] = 1;
                        $stats[$cat]['taken'] = 0;
                    } else {
                        $stats[$cat]['freq']++;
                    }
                    $rowData[] = $cat;
                } else if ($c == 1) {
                    if (strlen($data[$c]) < $minMasterbrainLength) {
                        $skip = true;
                        break;
                    }
                    $rowData [] = $data[$c];
                }
            }
            if (!$skip) {
                fputcsv($handleClean, $rowData);
            }
        }
        file_put_contents($statsFile, json_encode($stats));
        fclose($handle);
        fclose($handleClean);
    }
}
//Filter Data
$handleClean = openFile("database_cleaned.csv", "r");
$handleFilterTrain = openFile("database_cleaned_filtered_train.csv", "w");
$handleFilterTest = openFile("database_cleaned_filtered_test.csv", "w");
$row = 1;

echo "\r\nCalculating training portions and testing ones... \r\n";
//create training thresholds
foreach ($stats as $key => $value) {
    if ($key % 100 == 0) {
        echo '.';
    }
    $freq = ($stats[$key]['freq'] >= $threshold_max) ? $threshold_max : $stats[$key]['freq'];
    $stats[$key]['training_threshold'] = $freq * $trainingPercentage;
}

echo "\r\nSeperating training set from testing one, while considering thresholds... \r\n";
//load data into files
if ($handleClean !== FALSE) {
    while (($data = fgetcsv($handleClean)) !== FALSE) {
        $num = count($data);
        $row++;
        $rowData = [];
        $skip = false;
        $destination = $handleFilterTrain;
        if ($row % 1000 == 0) {
            echo '.';
        }
        for ($c = 0; $c < $num; $c++) {
            if ($c == 0) {
                $category = $data[$c];
                if ($stats[$category]['freq'] > $threshold_min && $stats[$category]['taken'] < $threshold_max) {
                    if ($stats[$category]['taken'] < $stats[$category]['training_threshold']) {
                        $destination = $handleFilterTrain;
                    } else {
                        $destination = $handleFilterTest;
                    }
                    $rowData[] = $category;
                    $stats[$category]['taken']++;
                } else {
                    $skip = true;
                    break;
                }
            } else {
                $rowData [] = $data[$c];
            }
        }
        if (!$skip) {
            fputcsv($destination, $rowData);
        }
    }
    fclose($handleFilterTrain);
    fclose($handleFilterTest);
    fclose($handleClean);
}


?>
