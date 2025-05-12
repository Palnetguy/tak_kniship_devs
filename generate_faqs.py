from tak_devs_app.models import FAQ
from django.db import transaction

# Delete existing FAQs if you want to start fresh
# FAQ.objects.all().delete()

faqs_data = [
    {
        "title": "What services does TAK Kinship offer?",
        "description": "TAK Kinship Technologies provides a comprehensive range of software development services including mobile app development (iOS and Android), web application development, desktop software solutions, UI/UX design, and technical consulting. We specialize in custom software solutions tailored to meet the specific needs of businesses across various industries."
    },
    {
        "title": "How much does it cost to build a custom application?",
        "description": "The cost of developing custom software depends on several factors including project complexity, features required, platforms supported, and timeline. We work with clients to understand their requirements and budget constraints before providing a detailed quote. Our pricing is transparent with no hidden costs, and we offer flexible engagement models including fixed-price projects and time-and-materials arrangements."
    },
    {
        "title": "How long does it take to develop a typical application?",
        "description": "Development timelines vary based on project scope and complexity. A simple mobile app might take 1-3 months, while a complex enterprise web application could take 3+ months. During our initial consultation, we'll assess your requirements and provide a realistic timeline. We follow an agile methodology that allows for iterative development and regular releases, ensuring you can see progress throughout the development process."
    },
    {
        "title": "What technologies do you specialize in?",
        "description": "Our team has expertise in a wide range of technologies. For web development, we work with React, Next.js, Django, and Node.js. For mobile apps, we use mostly Flutter while Swif and Kotlin at request. Our desktop applications are built with Flutter, Python.. We also have experience with database technologies including PostgreSQL, MongoDB, MySQL, and Firebase."
    },
    {
        "title": "Do you provide ongoing maintenance and support after project completion?",
        "description": "Yes, we offer comprehensive post-launch support and maintenance packages for all our projects. These include bug fixes, security updates, performance optimization, and feature enhancements. We can tailor a support package to your specific needs, whether that's monthly maintenance, on-demand support, or a dedicated support team."
    },
    {
        "title": "How do you ensure the quality of your deliverables?",
        "description": "Quality assurance is integrated throughout our development process. We implement automated testing, manual testing, code reviews, and continuous integration to catch issues early. Before launch, applications undergo rigorous testing across different devices and environments. We also involve clients in user acceptance testing to ensure the final product meets all requirements and expectations."
    },
    {
        "title": "What is your development process?",
        "description": "We follow an agile development methodology with these key phases: 1) Discovery and Planning - understanding requirements and creating specifications, 2) Design - creating wireframes and visual designs, 3) Development - building the application in sprints, 4) Testing - ensuring quality and functionality, 5) Deployment - launching the application, and 6) Maintenance - providing ongoing support and updates. Throughout this process, we maintain regular communication and provide access to project management tools to keep you informed."
    },
    {
        "title": "Do you sign NDAs to protect client ideas and information?",
        "description": "Absolutely. We understand the importance of confidentiality in the tech industry. We're happy to sign Non-Disclosure Agreements (NDAs) before discussing your project details. Protecting your intellectual property and business information is a priority for us, and we have strict internal policies to ensure client data security."
    },
    {
        "title": "Can you work with our existing team or systems?",
        "description": "Yes, we're experienced in collaborative development and system integration. We can augment your existing team with our specialists, work alongside other vendors, or integrate with your current systems. Our developers are adept at adapting to established codebases and workflows, ensuring a smooth collaboration process."
    },
    {
        "title": "What sets TAK Kinship apart from other development companies?",
        "description": "What distinguishes us is our commitment to forming true partnerships with our clients rather than just being service providers. We take time to understand your business goals, not just technical requirements. Our team combines technical excellence with creative problem-solving and business acumen. We're focused on building solutions that deliver real business value, not just fulfilling technical specifications. Additionally, our diverse team brings perspectives from different industries and backgrounds, enriching our approach to solving complex problems."
    },
    {
        "title": "Do you offer UI/UX design services?",
        "description": "Yes, we have a dedicated UI/UX design team that creates intuitive, engaging, and accessible user experiences. Our design process includes user research, creating personas, journey mapping, wireframing, prototyping, and usability testing. We follow design systems methodology to ensure consistency across platforms while adhering to platform-specific guidelines for native feel."
    },
    {
        "title": "What is your payment structure?",
        "description": "We typically structure payments in milestones tied to project deliverables. For longer projects, this might include an initial deposit, payments at key development stages, and a final payment upon project completion. For ongoing work or retainer arrangements, we bill monthly. We accept various payment methods including bank transfers and major credit cards."
    },
    {
        "title": "How do you handle project changes or scope adjustments?",
        "description": "We understand that requirements can evolve during development. Our agile approach accommodates changes through a structured change request process. When new requirements arise, we evaluate the impact on timeline and budget, provide detailed estimates, and implement changes only after client approval. This ensures transparency while maintaining project momentum."
    },
    {
        "title": "Are you available for emergency support or time-sensitive projects?",
        "description": "Yes, we have the capacity to handle urgent requests and time-sensitive projects. For existing clients, we offer emergency support services with defined response times. For new time-sensitive projects, we can allocate dedicated resources and implement expedited workflows while maintaining quality standards. Contact us immediately to discuss your urgent needs."
    },
    {
        "title": "Do you provide consulting services for startups?",
        "description": "Absolutely. We offer specialized consulting services for startups, including technical strategy development, MVP planning, technology stack selection, scalability planning, and investment preparation. Our experienced team can help validate your ideas, refine your product vision, and chart the most efficient path to market. We're passionate about helping startups succeed and can tailor our services to fit early-stage budget constraints."
    }
]

def create_faqs():
    with transaction.atomic():
        for faq_data in faqs_data:
            FAQ.objects.create(
                title=faq_data['title'], 
                description=faq_data['description']
            )
        print(f"Successfully created {len(faqs_data)} FAQs")

if __name__ == "__main__":
    create_faqs()