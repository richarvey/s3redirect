## **s3redirect**

A complete rewrite of a cli tool to become a fully fledge serverless and databaseless application that allows users to create a tiny URL by creating "Web Site Redirects" using Amazon S3, Lambda and Cloudfront.

You can use the service hosted on https://s3r.io for free or host your own. Please consider donating to the project to help support me plan ting trees for climate change!

**CLOUDFORMATION/CDK COMING SOON**

### **Requirements**

    AWS Account

### **S3 and CloudFront setup**

Create an S3 bucket via the console or command line tools and enable *Static Website Hosting*. You need to enable the static website hosting to allow the 302 redirects to be served otherwise you'll just find that you don't get redirected and your browser just trys to download a null file.

At this point make a note of the URL for your S3 hosted site.

You could just choose a FQDN name for the bucket and serve content directly from this setup. However if you want to make this scale you'll want to add Amazon CloudFront into the equation.

Open the the CloudFront tab in the the AWS console and click create new distribution. Select download as the distribution method and click continue. When you click on the *Origin Domain Name* It will highlight all the S3 buckets you have. **DO NOT** select these otherwise you'll break the serving of the 302 redirects again. Instead enter the URL of the *Static Website Hostsed bucket* you made a note of earlier. The Origin ID can be anything you want and its best just to go with the default.

The next set of options can be left as standard the only one that will be really important to you is the *Alternative Domain Names (CNAMES)* section where you get teh chance to tweak the URL you access your distribution on. When you are happy with your settings click Create Distribution and wait for the config to propergate to all the CloudFront edge nodes.

Enable SSL and use ACM to generate you a new certificate.

### **Lambda + API Gateway setup**

First thing first lets install our lambda. The code is in this repository in the file **lambda_function.py**. Create a new lambda in the console using the python 3.7 runtime. For the IAM permissions you need the basic execute functions and then to add this policy (you can do this as a policy attachment or inline).

You'll need to tweak the policy to match your S3 bucket name you created in the last section:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:DeleteObjectTagging",
                "s3:ListBucketByTags",
                "s3:GetBucketTagging",
                "s3:GetBucketWebsite",
                "s3:GetObjectVersionTagging",
                "s3:ListBucketVersions",
                "s3:GetBucketLogging",
                "s3:ListBucket",
                "s3:GetAccelerateConfiguration",
                "s3:GetBucketNotification",
                "s3:GetObjectVersionTorrent",
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "s3:PutBucketNotification",
                "s3:PutBucketTagging",
                "s3:GetBucketCORS",
                "s3:GetObjectTagging",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:GetBucketLocation",
                "s3:PutObjectAcl",
                "s3:GetObjectVersion"
            ],
            "Resource": [
                "arn:aws:s3:::<YOUR_BUCKET>/*",
                "arn:aws:s3:::<YOUR_BUCKET>"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:HeadBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

Now make sure you copy the code from **lambda_function.py** into the console and save the function.

Now in the triggers section of the console you'll need to add a API Gateway integration. You'll want to use __default__ for the stage and you'll need to create a method called **/create** this should be of type **POST** (enable CORS)

Make sure you enable CORS for this method. Now under **Method Execution** we need to set a mapping to get the right information into the lambda function from the front end. Create a new mapping with the type:

__application/x-www-form-urlencoded__

Enter the following mapping into the new field. This is responsible for transforming our post fromt he web frontend to the values needed by the lambda.

```
{
    "body-json": {
        #foreach( $token in $input.path('$').split('&') )
            #set( $keyVal = $token.split('=') )
            #set( $keyValSize = $keyVal.size() )
            #if( $keyValSize >= 1 )
                #set( $key = $util.urlDecode($keyVal[0]) )
                #if( $keyValSize >= 2 )
                    #set( $val = $util.urlDecode($keyVal[1]) )
                #else
                    #set( $val = '' )
                #end
                "$key": "$val"#if($foreach.hasNext),#end
            #end
        #end
    }
}
```

Deploy the API gateway and copy the invoke rule (API_GATEWAY_URL). you'll need this for setting up the frontend.

### **Deploy the frontend**

In this directory there are two files:

- **index.html**
- **style.css**

First you need to edit **index.html** and update the following values:

- **\<API\_GATEWAY\_URL\>**
- **\<BUCKET\_NAME\>**
- **\<URL\>** x3

Once you've edited **index.html** upload that and **style.css** to the S3 bucket you created and then make them public.

Now browse to your URL and you should be up and running.