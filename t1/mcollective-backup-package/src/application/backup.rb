module MCollective
  class Application
    class Backup<MCollective::Application
      # A backup plugin for functions pertaining to the backup system
      # 
      # Author: Ken Salanio <kssalanio@gmail.com>
      
      description "MCollective custom application to manage backup of CloudTop servers"

      usage <<-END_OF_USAGE
mco backup [OPTIONS] [FILTERS] <ACTION> <PACKAGE>
Usage: mco backup <echo|status|files|manual|restore>

The ACTION can be one of the following:

    echo        - test action, echos back sent message
    status      - status of backups
    files       - list of available backup files
    manual      - create a manual backup of specified node (requires -I filter)
    restore     - restore to a backup of specified node (requires -I filter)
    failed      - list of scheduled backups that have failed 
    
END_OF_USAGE

      option :message,
             :description    => "Message to send",
             :arguments      => ["-m", "--message MESSAGE"],
             :type           => String
      
      def handle_message(action, message, *args)
        messages = {1 => 'Please specify action\n',
                    2 => "Action has to be one of %s\n",
                    3 => "The action 'manual' or 'restore' requires an identity filter (-I)\n" }
        send(action, messages[message] % args)
      end

      def post_option_parser(configuration)
        if ARGV.size < 1
          handle_message(:raise, 1)
        else

          valid_actions = ['echo', 'status', 'files', 'manual', 'restore', 'failed']

          action = ARGV.shift
          
          if action =~ /^echo$/
            arguments = {:msg => configuration[:message]}
          elsif action =~  /^status$/
            arguments = {}
          elsif action =~  /^files$/
            arguments = {}
          elsif action =~  /^manual$/
            arguments = {}
          elsif action =~  /^restore$/
            arguments = {:backup_file => configuration[:message]}
          elsif action =~  /^failed$/
            arguments = {}
          else
            handle_message(:raise, 2, valid_actions.join(', '))
          end
          
          configuration[:action] = action
          configuration[:arguments] = arguments
        end
      end

      def validate_configuration(configuration)
        if configuration[:action] == 'manual' or configuration[:action] == 'restore'
          if Util.empty_filter?(options[:filter]) && !configuration[:yes] or options[:filter]["identity"].empty?
            handle_message(:print, 3)

            STDOUT.flush
            exit(1) #unless STDIN.gets.strip.match(/^(?:y|yes)$/i)
          end
        end
      end

      def main
        backup = rpcclient("backup")
        backup_result = backup.send(configuration[:action], configuration[:arguments])

        sender_width = backup_result.map{|s| s[:sender]}.map{|s| s.length}.max + 3
        pattern = "%%%ds: %%s" % sender_width

        puts
        puts "------------------------------------------------------------"
        puts

        backup_result.each do |result|
          if result[:statuscode] == 0
            unless backup.verbose
              puts(pattern % [result[:sender], result[:data][:ensure]])
              puts
              puts "------------------------------------------------------------"
              puts
            else
              case configuration[:action]
              when 'echo'
                puts "(%s)" % [result[:sender]]
                puts
                puts "       Message: %s" % [result[:data][:msg]]
                puts "    Reply Time: %s" % [result[:data][:time]]
                puts
                puts "------------------------------------------------------------"
                puts
                
              when 'status'
                puts "(%s)" % [result[:sender]]
                puts
                puts "               Backup Status: %s" % [result[:data][:status]]
                puts "    No. of scheduled backups: %s" % [result[:data][:scheduled_backups]]
                puts "       No. of Manual backups: %s" % [result[:data][:manual_backups]]
                puts
                puts "------------------------------------------------------------"
                puts
                
              when 'files'
                puts "(%s)" % [result[:sender]]
                puts
                puts "    List of backup files:"
                if result[:data][:files].nil?
                  puts "    [ERROR]: %s" % result[:data][:err]
                elsif result[:data][:files].empty?
                  puts "    No backup files found!"
                else
                  for file in result[:data][:files]
                    puts "    %s" % file
                  end
                end
                puts
                puts "------------------------------------------------------------"
                puts
                 
              when 'manual'
                puts "(%s)" % [result[:sender]]
                puts
                puts "    Manual backup result:"
                puts "    * %s" % result.results[:data][:result]
                puts
                puts "------------------------------------------------------------"
                puts
                
              when 'restore'
                puts "(%s)" % [result[:sender]]
                puts
                puts "    Remote restore result:"
                puts "    * %s" % result.results[:data][:result]
                puts
                puts "------------------------------------------------------------"
                puts
                
              when 'failed'
                puts "(%s)" % [result[:sender]]
                puts
                puts "    List of failed scheduled backups:"
                if result[:data][:failed_backups].nil?
                  puts "    [ERROR]: %s" % result[:data][:err]
                elsif result[:data][:failed_backups].empty?
                  puts "    *  No failures for this node"
                else
                  for failure in result[:data][:failed_backups]
                    puts "    %s" % failure
                  end
                end
                puts
                puts "------------------------------------------------------------"
                puts
                
              end
            end
          else
            width = 60
            puts "(%s) - [ERROR ENCOUNTERED]" % [result[:sender]]
            puts
            puts result[:statusmsg].scan(/\S.{0,#{width}}\S(?=\s|$)|\S+/)
            puts
            puts "------------------------------------------------------------"
            puts
          end
        end

        puts
        printrpcstats :summarize => true, :caption => "%s Backup results" % configuration[:action]
        halt(backup.stats)
      end
    end
  end
end

