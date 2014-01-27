metadata :name        => "backup",
         :description => "Backup service for CloudTop MCollective",
         :author      => "Ken Salanio",
         :license     => "GPLv2",
         :version     => "1.0",
         :url         => "http://www.cloudtop.ph",
         :timeout     => 1000


action "status", :description => "Prints the backup status and the number of scheduled/manual backup files" do
     display :always

     output :scheduled_backups,
           :description => "Number of files from scheduled backups",
           :display_as => "Number of scheduled backup files:"

     output :manual_backups,
           :description => "Number of files from manual backups",
           :display_as => "Number of manual backup files:"

     output :status,
           :description => "Status of latest backup",
           :display_as => "Status of latest backup:"

     output :err,
           :description => "Errors encountered",
           :display_as => "Errors: "
end

action "files", :description => "Prints out the list of backup files in the node's archive" do
     display :always

     output :files,
           :description => "List of backup files",
           :display_as => "Backup files of this node:"

     output :err,
           :description => "Errors encountered",
           :display_as => "Errors: "
end

action "manual", :description => "Manually create a backup file at the target host name. Required filters: [identity]" do
     display :always

     output :result,
           :description => "Result of manual backup",
           :display_as => "Manual backup result: "

     output :err,
           :description => "Errors encountered",
           :display_as => "Errors: "
end

action "restore", :description => "Restores to specified backup archive. Required filters: [identity]" do
     display :always

     input :backup_file,
           :prompt      => "Backup file",
           :description => "The archived file to restore from",
           :type        => :string,
           :validation  => '^[a-zA-Z\/\.\-_\d]+$',
           :optional    => false,
           :maxlength   => 100

     output :result,
           :description => "Result of restore",
           :display_as => "Restore result: "

     output :err,
           :description => "Errors encountered",
           :display_as => "Errors: "

end

action "failed", :description => "Prints out the list failed scheduled backups" do
     display :always

     output :failed_backups,
           :description => "List of failed scheduled backups",
           :display_as => "Failed scheduled backups: "

     output :err,
           :description => "Errors encountered",
           :display_as => "Errors: "
end

