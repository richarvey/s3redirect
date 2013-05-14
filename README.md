## **s3redirect**

A simple script to set up objects in Amazon S3 with the meta data for web redirects, allowing you to build a massively scalable URL shortening/redirecting service.

### **Requirements**

You'll require the following installed to run the s3redirect scripts.

    Python
    Lib boto 2.7.3+
    AWS Account

### **S3 and CloudFront setup**

Create an S3 bucket via the console or command line tools and enable *Static Website Hosting*. You need to enable the static website hosting to allow the 302 redirects to be served otherwise you'll just find that you don't get redirected and your browser just trys to download a null file.

At this point make a note of the URL for your S3 hosted site.

At this point you could just choose a sensible name for the bucket and serve content directly from this setup. However if you want to make this scale you'll want to add Amazon CloudFront into the equation.

Open the the CloudFront tab in the the AWS console and click create new distribution. Select download as the distribution method and click continue. When you click on the *Origin Domain Name* It will highlight all the S3 buckets you have. **DO NOT** select these otherwise you'll break the serving of the 302 redirects again. Instead enter the URL of the *Static Website Hostsed bucket* you made a note of earlier. The Origin ID can be anything you want and its best just to go with the default.

The next set of options can be left as standard the only one that will be really important to you is the *Alternative Domain Names (CNAMES)* section where you get teh chance to tweak the URL you access your distribution on. When you are happy with your settings click Create Distribution and wait for the config to propergate to all the CloudFront edge nodes.

You are now ready to use the tool to create your redirects. 

### **Config File Format**

Before using the s3redirect script you'll need to set up your config file with your AWS credentials and the target bucket name.

The default config which is *.s3redirect*, should contain the following information which you'll need to update with your details.

    [s3redirect]
    AWS_ACCESS_KEY_ID=<Your Access Key>
    AWS_SECRET_ACCESS_KEY=<Your Secret Key>
    bucket_name=<Your Bucket name>
    cloudfront_id=<The ID of your configured cloudfront distro> **Optional

*cloudfront_id* is optional and will create invalidation requests for objects if updated or deleted from your redirect store 

However if you want to support multiple buckets you can expand the config like so:

    [s3redirect]
    AWS_ACCESS_KEY_ID=<Your Access Key>
    AWS_SECRET_ACCESS_KEY=<Your Secret Key>
    bucket_name=<Your Bucket name>
    
    [second_config]
    AWS_ACCESS_KEY_ID=<Your Access Key>
    AWS_SECRET_ACCESS_KEY=<Your Secret Key>
    bucket_name=<Your Bucket name>

Then by specifying the -c flag on the command line you can choose between the two sets of credentials. The -c flag requires an argument which is the name of the config block, so for example *second_config*. If you dont specify a config block s3redirect will be automatically used.

***NOTE:*** I highly recomend you create a separate IAM account and lock down the S3 privilages and use these credentials in your config file.

### **Example Usage**

Create a redirect from moo to http://www.squarecows.com:

    user@box01:~/dev/s3redirect$ ./s3redirect -r moo -u http://www.squarecows.com

    Creating Redirect moo in Amazon S3 bucket aws-c4-url-beta to http://www.squarecows.com

Update a redirect from moo to http://blog.squarecows.com:
    
    user@box01:~/dev/s3redirect$ ./s3redirect -r moo -u http://blog.squarecows.com

    Redirect for moo already exists to location http://www.squarecows.com
    Do you wish to continue? [y/N] y
    Updating current redirect moo in Amazon S3 bucket aws-c4-url-beta to http://blog.squarecows.com

Delete a redirect called *test*:

    user@box01:~/dev/s3redirect$ ./s3redirect -d test
    
    Redirect for test currently points to location http://blog.squarecows.com
    Do you really wish to delete? [y/N] y
    Deleting redirect test in Amazon S3 bucket aws-c4-url-beta


#### **Using alternative config settings**
    
Create a redirect using other config settings:

    user@box01:~/dev/s3redirect$ ./s3redirect -c second_config -r moo -u http://blog.squarecows.com

    Creating Redirect moo in Amazon S3 bucket los.io to http://blog.squarecows.com

Update a redirect using alternative configs but choose to abort:

    user@box01:~/dev/s3redirect$ ./s3redirect -c second_config -r moo -u http://www.squarecows.com

    Redirect for moo already exists to location http://blog.squarecows.com
    Do you wish to continue? [y/N] n
    Not updating

Delete a redirect called *test* using an alternative config:

    user@box01:~/dev/s3redirect$ ./s3redirect -c second_config -d test
    
    Redirect for test currently points to location http://blog.squarecows.com
    Do you really wish to delete? [y/N] y
    Deleting redirect test in Amazon S3 bucket aws-c4-url-beta

#### **Override default upper/lower case behaviour**

By default s3redirect will create multiple versions of the redirect object to handle people entering capitalised versions of the URL for example.

    user@box01:~/dev/s3redirect$ ./s3redirect  -r testmoo -u http://blog.squarecows.com

The command above will result in creating an object called testmoo and one called TESTMOO.

    user@box01:~/dev/s3redirect$ ./s3redirect  -r TestMoo -u http://blog.squarecows.com

However if you choose to mix upper and lower case in your command line like above you will end up with three objects, TestMoo, testmoo and TESTMOO.

To override this default behaviour specify ***-p False*** on the command line.

### **TODO**

Please See: https://github.com/richarvey/s3redirect/blob/master/TODO.md

14 May 2013
