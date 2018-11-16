BEGIN {
    RS = "--";
    FS = "\t";
}
{
     print $48 "\t" $50 "\t" $70 "\n"
}
END {
}
