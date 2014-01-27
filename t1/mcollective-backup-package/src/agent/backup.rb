module MCollective
  module Agent
    class Backup<RPC::Agent
      # A backup agent for functions pertaining to the backup system
      # 
      # Author: Ken Salanio <kssalanio@gmail.com>
      
      #STATUS
      action "status" do
        out = ""
        status = run("/shared/scripts/backup/backup_status.sh", :stdout => out, :stderr => :err, :chomp => true)
        tokens = out.split("/")
        reply[:scheduled_backups] = tokens[0]
        reply[:manual_backups] = tokens[1]
        reply[:status] = tokens[2]
      end

      #FILES
      action "files" do
        out = ""
        status = run("/shared/scripts/backup/backup_status.sh -F", :stdout => out, :stderr => :err, :chomp => true)
        reply[:files] = out.split(" ")
      end

      #MANUAL
      action "manual" do
        out = ""
        status = run("/shared/scripts/backup/backup_manual.sh", :stdout => out, :stderr => :err, :chomp => true)
        reply[:result] = out
      end

      #RESTORE
      action "restore" do
        validate :backup_file, String

        backup_file=request[:backup_file]

        if File.exist?(backup_file)
          out=""
          status = run("/shared/scripts/backup/backup_restore.sh #{backup_file}", :stdout => out, :stderr => :err, :chomp => true)
          reply[:result] = out
          reply[:status] = status 
        else
          reply[:err] = "File #{backup_file} does not exist!"
        end
      end

      #FAILED
      action "failed" do
        failed_log_file = "/var/archive/failed.log"
        if File.exist?(failed_log_file)
          fail_list = []
          File.read(failed_log_file).each_line do |line|
            fail_list << line.chop
          end
          reply[:failed_backups] = fail_list
        else
          reply[:err] = "File [#{failed_log_file}] does not exist!"
        end
      end

    end
  end
end

